from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from app.utils.geo import calculate_distance_km
from app.models.event_post import EventPost
from app.models.user import User
from app.models.location import City
from app.schemas.event_post import EventPostCreate, EventPostUpdate
from app.services.notification_service import notification_service

from app.models.vendor import VendorProfile, VendorCategoryMap, VendorCategory

from app.models.event_post_item import EventPostItem
from app.models.quote import Quote
from datetime import datetime

class EventPostService_:

    def create_post(self, db: Session, customer_id: int, data: EventPostCreate):
        items_data = data.items
        payload = data.model_dump(exclude={"items"})

        post = EventPost(customer_id=customer_id, **payload)
        db.add(post)
        db.flush()

        for item in items_data:
            db.add(EventPostItem(
                event_post_id=post.id,
                category_id=item.category_id,
                budget_amount=item.budget_amount
            ))

        db.commit()
        db.refresh(post)

        self._notify_nearby_vendors(db, post)

        return self._attach_customer_name(db, post)


    def update_post(self, db: Session, customer_id: int, post_id: int, data: EventPostUpdate):
        post = db.query(EventPost).filter(
            EventPost.id == post_id,
            EventPost.customer_id == customer_id
        ).first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        update_data = data.model_dump(exclude_unset=True, exclude={"items"})
        for field, value in update_data.items():
            setattr(post, field, value)

        if data.items is not None:
            db.query(EventPostItem).filter(EventPostItem.event_post_id == post.id).delete()
            for item in data.items:
                db.add(EventPostItem(
                    event_post_id=post.id,
                    category_id=item.category_id,
                    budget_amount=item.budget_amount
                ))

        db.commit()
        db.refresh(post)
        return self._attach_customer_name(db, post)


    def list_posts_for_vendor(
        self, db: Session,
        vendor_state_id, vendor_city_id,
        filter_state_id=None, filter_city_id=None,
        sort_by_event_type: int = None,   # ← new: filter/sort by a specific event_type/category id
        skip: int = 0, limit: int = 20
    ):
        query = db.query(EventPost).filter(EventPost.is_active == True)

        if filter_state_id or filter_city_id:
            if filter_state_id:
                city_ids_in_state = db.query(City.id).filter(City.state_id == filter_state_id).subquery()
                query = query.filter(EventPost.city_id.in_(city_ids_in_state))
            if filter_city_id:
                query = query.filter(EventPost.city_id == filter_city_id)
        else:
            if vendor_city_id:
                query = query.filter(EventPost.city_id == vendor_city_id)
            elif vendor_state_id:
                city_ids_in_state = db.query(City.id).filter(City.state_id == vendor_state_id).subquery()
                query = query.filter(EventPost.city_id.in_(city_ids_in_state))

        if sort_by_event_type:
            # Match posts whose single category OR any multi-item category matches
            post_ids_with_item = db.query(EventPostItem.event_post_id).filter(
                EventPostItem.category_id == sort_by_event_type
            ).subquery()
            query = query.filter(
                (EventPost.category_id == sort_by_event_type) |
                (EventPost.id.in_(post_ids_with_item))
            )

        query = query.order_by(EventPost.created_at.desc())
        posts = query.offset(skip).limit(limit).all()

        return [self._attach_customer_name(db, p) for p in posts]


    def _attach_customer_name(self, db: Session, post: EventPost):
        customer = db.query(User).filter(User.id == post.customer_id).first()
        post.customer_name = customer.name if customer else "Customer"

        if post.category_id:
            category = db.query(VendorCategory).filter(VendorCategory.id == post.category_id).first()
            post.category_name = category.name if category else None
        else:
            post.category_name = None

        items = db.query(EventPostItem).filter(EventPostItem.event_post_id == post.id).all()
        for item in items:
            cat = db.query(VendorCategory).filter(VendorCategory.id == item.category_id).first()
            item.category_name = cat.name if cat else None
        post.items = items

        post.quote_count = db.query(Quote).filter(Quote.event_post_id == post.id).count()

        post.is_expired = bool(post.response_deadline and post.response_deadline < datetime.utcnow())

        return post
    def _notify_nearby_vendors(self, db: Session, post: EventPost):
        """
        Sends a notification to approved vendors located in the same city
        (falling back to same state) as the new event post. If the post
        specifies a category, notifications are further narrowed to only
        vendors who offer that category of service — this prevents
        notification spam to irrelevant vendors as the platform scales.
        """
        if not post.city_id and not post.state_id:
            return

        query = db.query(VendorProfile).filter(
            VendorProfile.is_approved == True
        )

        if post.city_id:
            query = query.filter(VendorProfile.city_id == post.city_id)
        elif post.state_id:
            city_ids_in_state = db.query(City.id).filter(
                City.state_id == post.state_id
            ).subquery()
            query = query.filter(VendorProfile.city_id.in_(city_ids_in_state))

        if post.category_id:
            vendor_ids_in_category = db.query(VendorCategoryMap.vendor_id).filter(
                VendorCategoryMap.category_id == post.category_id
            ).subquery()
            query = query.filter(VendorProfile.id.in_(vendor_ids_in_category))

        nearby_vendors = query.all()

        customer = db.query(User).filter(User.id == post.customer_id).first()
        customer_name = customer.name if customer else "A customer"

        for vendor in nearby_vendors:
            notification_service.create(
                db,
                user_id=vendor.user_id,
                title="New Event Posted Near You 📍",
                message=f'{customer_name} posted "{post.title}" in your area. Tap to view and message them.',
                type="event_post",
                link=f"/vendor/event-posts?highlight={post.id}"
            )


    def delete_post(self, db: Session, customer_id: int, post_id: int):
        post = db.query(EventPost).filter(
            EventPost.id == post_id,
            EventPost.customer_id == customer_id
        ).first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        db.delete(post)
        db.commit()
        return {"message": "Post deleted"}


    def get_my_posts(self, db: Session, customer_id: int):
        posts = db.query(EventPost).filter(
            EventPost.customer_id == customer_id
        ).order_by(EventPost.created_at.desc()).all()

        return [self._attach_customer_name(db, p) for p in posts]

    def get_post_by_id(self, db: Session, post_id: int):
        post = db.query(EventPost).filter(
            EventPost.id == post_id,
            EventPost.is_active == True
        ).first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        return self._attach_customer_name(db, post)

    def get_similar_vendors(self, db: Session, vendor_id: int, limit: int = 6):
        """
        Finds other approved vendors that are a good alternative to the one
        being viewed: same city preferred, falling back to same state, and
        matching at least one shared category where possible.
        """
        vendor = db.query(VendorProfile).filter(VendorProfile.id == vendor_id).first()
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")

        vendor_category_ids = [
            row.category_id for row in
            db.query(VendorCategoryMap.category_id).filter(VendorCategoryMap.vendor_id == vendor.id).all()
        ]

        query = db.query(VendorProfile).filter(
            VendorProfile.is_approved == True,
            VendorProfile.id != vendor.id
        )

        # Prefer same city
        same_city = query.filter(VendorProfile.city_id == vendor.city_id)
        if vendor_category_ids:
            same_city_ids = db.query(VendorCategoryMap.vendor_id).filter(
                VendorCategoryMap.category_id.in_(vendor_category_ids)
            ).subquery()
            same_city = same_city.filter(VendorProfile.id.in_(same_city_ids))

        results = same_city.order_by(VendorProfile.rank_score.desc()).limit(limit).all()

        # Fall back to same state if not enough same-city matches
        if len(results) < limit and vendor.city_id:
            city = db.query(City).filter(City.id == vendor.city_id).first()
            if city:
                remaining = limit - len(results)
                existing_ids = [v.id for v in results] + [vendor.id]
                city_ids_in_state = db.query(City.id).filter(City.state_id == city.state_id).subquery()
                fallback = db.query(VendorProfile).filter(
                    VendorProfile.is_approved == True,
                    VendorProfile.city_id.in_(city_ids_in_state),
                    ~VendorProfile.id.in_(existing_ids)
                ).order_by(VendorProfile.rank_score.desc()).limit(remaining).all()
                results.extend(fallback)

        for v in results:
            cover = db.query(VendorPhoto).filter(VendorPhoto.vendor_id == v.id, VendorPhoto.is_cover == True).first()
            if not cover:
                cover = db.query(VendorPhoto).filter(VendorPhoto.vendor_id == v.id).order_by(VendorPhoto.sort_order.asc()).first()
            v.cover_photo_url = cover.photo_url if cover else None

        return results
    def list_posts_nearby(self, db: Session, latitude: float, longitude: float, radius_km: float = 25, skip=0, limit=20):
        posts = db.query(EventPost).filter(
            EventPost.is_active == True,
            EventPost.latitude.isnot(None),
            EventPost.longitude.isnot(None)
        ).all()

        results = []
        for post in posts:
            distance = calculate_distance_km(latitude, longitude, post.latitude, post.longitude)
            if distance <= radius_km:
                post.distance_km = round(distance, 2)
                results.append(self._attach_customer_name(db, post))

        results.sort(key=lambda p: p.distance_km)
        return results[skip: skip + limit]

event_post_service = EventPostService_()