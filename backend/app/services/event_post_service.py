from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

from app.models.event_post import EventPost
from app.models.user import User
from app.models.location import City
from app.schemas.event_post import EventPostCreate, EventPostUpdate


class EventPostService_:

    def create_post(self, db: Session, customer_id: int, data: EventPostCreate):
        post = EventPost(
            customer_id=customer_id,
            **data.model_dump()
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        return self._attach_customer_name(db, post)


    def update_post(self, db: Session, customer_id: int, post_id: int, data: EventPostUpdate):
        post = db.query(EventPost).filter(
            EventPost.id == post_id,
            EventPost.customer_id == customer_id
        ).first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(post, field, value)

        db.commit()
        db.refresh(post)
        return self._attach_customer_name(db, post)


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


    def list_posts_for_vendor(
        self, db: Session,
        vendor_state_id: Optional[int],
        vendor_city_id: Optional[int],
        filter_state_id: Optional[int] = None,
        filter_city_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ):
        """
        Default behavior (no explicit filter applied): show only posts matching
        the VENDOR's own state and city first — this is the "initially show
        vendor's state/city posts only" requirement.

        If the vendor explicitly applies a filter_state_id/filter_city_id,
        that overrides the default and searches broader/different locations instead.
        """
        query = db.query(EventPost).filter(EventPost.is_active == True)

        if filter_state_id or filter_city_id:
            # Vendor has explicitly chosen to look elsewhere
            if filter_state_id:
                city_ids_in_state = db.query(City.id).filter(City.state_id == filter_state_id).subquery()
                query = query.filter(EventPost.city_id.in_(city_ids_in_state))
            if filter_city_id:
                query = query.filter(EventPost.city_id == filter_city_id)
        else:
            # Default: restrict to vendor's own city/state only
            if vendor_city_id:
                query = query.filter(EventPost.city_id == vendor_city_id)
            elif vendor_state_id:
                city_ids_in_state = db.query(City.id).filter(City.state_id == vendor_state_id).subquery()
                query = query.filter(EventPost.city_id.in_(city_ids_in_state))

        query = query.order_by(EventPost.created_at.desc())
        posts = query.offset(skip).limit(limit).all()

        # Batch-fetch all customer names in one query instead of one-per-post
        customer_ids = [p.customer_id for p in posts]
        customers = db.query(User).filter(User.id.in_(customer_ids)).all()
        customer_map = {c.id: c.name for c in customers}

        for post in posts:
            post.customer_name = customer_map.get(post.customer_id, "Customer")

        return posts


    def _attach_customer_name(self, db: Session, post: EventPost):
        customer = db.query(User).filter(User.id == post.customer_id).first()
        post.customer_name = customer.name if customer else "Customer"
        return post


event_post_service = EventPostService_()