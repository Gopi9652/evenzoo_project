from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from app.utils.geo import calculate_distance_km
from app.models.vendor import (
    VendorProfile, VendorService, VendorPhoto,
    VendorAvailability, VendorWorkingHours,
    VendorCategory, VendorCategoryMap,VendorCategory, VendorCategoryMap, VendorDocument
)
from app.models.user import User
from app.utils.cloudinary_client import delete_image
from app.schemas.vendor import (
    VendorProfileCreate, VendorProfileUpdate,
    VendorServiceCreate, VendorServiceUpdate,
    VendorPhotoCreate, VendorAvailabilityCreate,
    WorkingHoursCreate
)
from app.models.location import City
from app.models.review import Review
from typing import List
from app.models.vendor import VendorProfile, VendorPhoto, VendorService, VendorCategoryMap
from app.models.location import City
from app.utils.slug import generate_unique_slug
from app.models.vendor import VendorVideo
class VendorService_:

    # ── GET VENDOR PROFILE ──
    def get_profile(self, db: Session, user_id: int):
        vendor = db.query(VendorProfile).filter(
            VendorProfile.user_id == user_id
        ).first()

        if not vendor:
            raise HTTPException(
                status_code=404,
                detail="Vendor profile not found"
            )
        return vendor

    def get_profile_by_id(self, db: Session, vendor_id: int):
        vendor = db.query(VendorProfile).filter(
            VendorProfile.id == vendor_id
        ).first()

        if not vendor:
            raise HTTPException(
                status_code=404,
                detail="Vendor not found"
            )

        cover = db.query(VendorPhoto).filter(
            VendorPhoto.vendor_id == vendor.id,
            VendorPhoto.is_cover == True
        ).first()

        if not cover:
            cover = db.query(VendorPhoto).filter(
                VendorPhoto.vendor_id == vendor.id
            ).order_by(VendorPhoto.sort_order.asc()).first()

        vendor.cover_photo_url = cover.photo_url if cover else None

        # Attach phone number from the linked User account for WhatsApp deep-linking
        user = db.query(User).filter(User.id == vendor.user_id).first()
        #vendor.whatsapp_number = user.phone if user else None
        vendor.whatsapp_number = user.phone if (user and vendor.show_whatsapp) else None

        return vendor


    # ── UPDATE VENDOR PROFILE ──
    def update_profile(self, db: Session, user_id: int, data: VendorProfileUpdate):
        vendor = db.query(VendorProfile).filter(VendorProfile.user_id == user_id).first()
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor profile not found")

        update_data = data.model_dump(exclude_unset=True)
        old_name = vendor.business_name

        for field, value in update_data.items():
            setattr(vendor, field, value)

        # Regenerate slug only if the business name actually changed
        if "business_name" in update_data and update_data["business_name"] != old_name:
            vendor.slug = generate_unique_slug(db, vendor.business_name)

        db.commit()
        db.refresh(vendor)
        return vendor
    def list_vendors(
        self,
        db: Session,
        state_id: Optional[int] = None,
        city_id: Optional[int] = None,
        category_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ):
        # =========================================================
        # 1. BASE VENDOR QUERY
        # =========================================================

        query = db.query(VendorProfile).filter(
            VendorProfile.is_approved == True
        )

        # =========================================================
        # 2. STATE FILTER
        # =========================================================

        if state_id:
            city_ids_in_state = (
                db.query(City.id)
                .filter(City.state_id == state_id)
                .subquery()
            )

            query = query.filter(
                VendorProfile.city_id.in_(city_ids_in_state)
            )

        # =========================================================
        # 3. CITY FILTER
        # =========================================================

        if city_id:
            query = query.filter(
                VendorProfile.city_id == city_id
            )

        # =========================================================
        # 4. CATEGORY FILTER
        # =========================================================

        if category_id:
            vendor_ids_subquery = (
                db.query(VendorCategoryMap.vendor_id)
                .filter(
                    VendorCategoryMap.category_id == category_id
                )
                .subquery()
            )

            query = query.filter(
                VendorProfile.id.in_(vendor_ids_subquery)
            )

        # =========================================================
        # 5. SORT + PAGINATION
        # =========================================================

        query = query.order_by(
            VendorProfile.rank_score.desc()
        )

        vendors = (
            query
            .offset(skip)
            .limit(limit)
            .all()
        )

        # No vendors found
        if not vendors:
            return []

        # =========================================================
        # 6. GET ALL VENDOR IDS
        # =========================================================

        vendor_ids = [
            vendor.id
            for vendor in vendors
        ]

        # =========================================================
        # 7. GET ALL PHOTOS IN ONE QUERY
        #
        # Priority:
        #   1. is_cover = True
        #   2. lowest sort_order
        #
        # Therefore the first photo for each vendor becomes
        # the cover/fallback photo.
        # =========================================================

        photos = (
            db.query(VendorPhoto)
            .filter(
                VendorPhoto.vendor_id.in_(vendor_ids)
            )
            .order_by(
                VendorPhoto.vendor_id.asc(),
                VendorPhoto.is_cover.desc(),
                VendorPhoto.sort_order.asc()
            )
            .all()
        )

        # =========================================================
        # 8. GET ALL ACTIVE SERVICES IN ONE QUERY
        # =========================================================

        services = (
            db.query(VendorService)
            .filter(
                VendorService.vendor_id.in_(vendor_ids),
                VendorService.is_active == True
            )
            .order_by(
                VendorService.vendor_id.asc(),
                VendorService.price.asc()
            )
            .all()
        )

        # vendor_id -> list of services
        services_by_vendor = {}

        for service in services:

            if service.vendor_id not in services_by_vendor:
                services_by_vendor[service.vendor_id] = []

            services_by_vendor[service.vendor_id].append(
                service
            )

        # =========================================================
        # 9. BUILD RESPONSE DATA
        #
        # IMPORTANT:
        # No database queries happen inside this loop.
        # =========================================================

        for vendor in vendors:


            # -----------------------------------------------------
            # Get services already loaded into memory
            # -----------------------------------------------------

            vendor_services = services_by_vendor.get(
                vendor.id,
                []
            )

            # -----------------------------------------------------
            # First 4 services for hover preview
            # -----------------------------------------------------

            vendor.services_preview = [
                {
                    "name": service.name,
                    "price": service.price
                }
                for service in vendor_services[:4]
            ]

            # -----------------------------------------------------
            # Total number of active services
            # -----------------------------------------------------

            vendor.service_count = len(
                vendor_services
            )

            # -----------------------------------------------------
            # Cheapest service
            #
            # Services were ordered by price ASC,
            # so the first service is the cheapest.
            # -----------------------------------------------------

            vendor.min_price = (
                vendor_services[0].price
                if vendor_services
                else None
            )

        # =========================================================
        # 10. RETURN VENDORS
        # =========================================================

        return vendors
    # ── ADD SERVICE ──
    def add_service(
        self, db: Session,
        user_id: int,
        data: VendorServiceCreate
    ):
        vendor = self.get_profile(db, user_id)

        service = VendorService(
            vendor_id=vendor.id,
            **data.model_dump()
        )
        db.add(service)
        db.commit()
        db.refresh(service)
        return service


    # ── UPDATE SERVICE ──
    def update_service(
        self, db: Session,
        user_id: int,
        service_id: int,
        data: VendorServiceUpdate
    ):
        vendor = self.get_profile(db, user_id)

        service = db.query(VendorService).filter(
            VendorService.id        == service_id,
            VendorService.vendor_id == vendor.id
        ).first()

        if not service:
            raise HTTPException(
                status_code=404,
                detail="Service not found"
            )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(service, field, value)

        db.commit()
        db.refresh(service)
        return service


    # ── DELETE SERVICE ──
    def delete_service(
        self, db: Session,
        user_id: int,
        service_id: int
    ):
        vendor = self.get_profile(db, user_id)

        service = db.query(VendorService).filter(
            VendorService.id        == service_id,
            VendorService.vendor_id == vendor.id
        ).first()

        if not service:
            raise HTTPException(
                status_code=404,
                detail="Service not found"
            )

        db.delete(service)
        db.commit()
        return {"message": "Service deleted"}


    # ── GET ALL SERVICES ──
    def get_services(self, db: Session, vendor_id: int):
        return db.query(VendorService).filter(
            VendorService.vendor_id == vendor_id,
            VendorService.is_active == True
        ).all()


    # ── ADD PHOTO ──
    def add_photo(
        self, db: Session,
        user_id: int,
        data: VendorPhotoCreate
    ):
        vendor = self.get_profile(db, user_id)

        # If this is cover photo remove old cover
        if data.is_cover:
            db.query(VendorPhoto).filter(
                VendorPhoto.vendor_id == vendor.id,
                VendorPhoto.is_cover  == True
            ).update({"is_cover": False})

        photo = VendorPhoto(
            vendor_id=vendor.id,
            **data.model_dump()
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)
        return photo


    # ── DELETE PHOTO ──
    def delete_photo(
        self, db: Session,
        user_id: int,
        photo_id: int
    ):
        vendor = self.get_profile(db, user_id)

        photo = db.query(VendorPhoto).filter(
            VendorPhoto.id        == photo_id,
            VendorPhoto.vendor_id == vendor.id
        ).first()
        
        if not photo:
            raise HTTPException(
                status_code=404,
                detail="Photo not found"
            )
        result = delete_image (photo.photo_url)
        db.delete(photo)
        db.commit()
        return {"message": "Photo deleted"}


    # ── GET PHOTOS ──
    def get_photos(self, db: Session, vendor_id: int):
        return db.query(VendorPhoto).filter(
            VendorPhoto.vendor_id == vendor_id
        ).order_by(VendorPhoto.sort_order).all()

    def get_profile_by_slug(self, db: Session, slug: str):
        vendor = db.query(VendorProfile).filter(VendorProfile.slug == slug).first()
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")

        cover = db.query(VendorPhoto).filter(
            VendorPhoto.vendor_id == vendor.id, VendorPhoto.is_cover == True
        ).first()
        if not cover:
            cover = db.query(VendorPhoto).filter(VendorPhoto.vendor_id == vendor.id).order_by(VendorPhoto.sort_order.asc()).first()
        vendor.cover_photo_url = cover.photo_url if cover else None

        user = db.query(User).filter(User.id == vendor.user_id).first()
        vendor.whatsapp_number = user.phone if (user and vendor.show_whatsapp) else None

        return vendor
    # ── SET AVAILABILITY ──
    def set_availability(
        self, db: Session,
        user_id: int,
        data: VendorAvailabilityCreate
    ):
        vendor = self.get_profile(db, user_id)

        # Check if date already exists
        existing = db.query(VendorAvailability).filter(
            VendorAvailability.vendor_id == vendor.id,
            VendorAvailability.date      == data.date
        ).first()

        if existing:
            existing.is_available = data.is_available
            existing.reason       = data.reason
            db.commit()
            db.refresh(existing)
            return existing

        availability = VendorAvailability(
            vendor_id=vendor.id,
            **data.model_dump()
        )
        db.add(availability)
        db.commit()
        db.refresh(availability)
        return availability


    # ── GET AVAILABILITY ──
    def get_availability(self, db: Session, vendor_id: int):
        return db.query(VendorAvailability).filter(
            VendorAvailability.vendor_id == vendor_id
        ).order_by(VendorAvailability.date).all()


    # ── SET WORKING HOURS ──
    def set_working_hours(
        self, db: Session,
        user_id: int,
        data: WorkingHoursCreate
    ):
        vendor = self.get_profile(db, user_id)

        existing = db.query(VendorWorkingHours).filter(
            VendorWorkingHours.vendor_id   == vendor.id,
            VendorWorkingHours.day_of_week == data.day_of_week
        ).first()

        if existing:
            for field, value in data.model_dump().items():
                setattr(existing, field, value)
            db.commit()
            db.refresh(existing)
            return existing

        hours = VendorWorkingHours(
            vendor_id=vendor.id,
            **data.model_dump()
        )
        db.add(hours)
        db.commit()
        db.refresh(hours)
        return hours


    # ── GET WORKING HOURS ──
    def get_working_hours(self, db: Session, vendor_id: int):
        return db.query(VendorWorkingHours).filter(
            VendorWorkingHours.vendor_id == vendor_id
        ).order_by(VendorWorkingHours.day_of_week).all()


    # ── GET CATEGORIES ──
    def get_categories(self, db: Session):
        return db.query(VendorCategory).filter(
            VendorCategory.is_active == True
        ).all()


    # ── ASSIGN CATEGORY TO VENDOR ──
    def assign_category(
        self, db: Session,
        user_id: int,
        category_id: int
    ):
        vendor = self.get_profile(db, user_id)

        # Check already assigned
        existing = db.query(VendorCategoryMap).filter(
            VendorCategoryMap.vendor_id   == vendor.id,
            VendorCategoryMap.category_id == category_id
        ).first()

        if existing:
            return {"message": "Category already assigned"}

        db.add(VendorCategoryMap(
            vendor_id=vendor.id,
            category_id=category_id
        ))
        db.commit()
        return {"message": "Category assigned"}
# ── REQUEST NEW CATEGORY (vendor suggests, pending admin approval) ──
    def request_custom_category(
            self, db: Session,
            user_id: int,
            name: str,
            description: str = None
        ):
            vendor = self.get_profile(db, user_id)

            # Check if it already exists (case-insensitive)
            existing = db.query(VendorCategory).filter(
                VendorCategory.name.ilike(name)
            ).first()

            if existing:
                # Just assign the existing one instead of duplicating
                return self.assign_category(db, user_id, existing.id)

            # Create as inactive until admin approves it
            new_category = VendorCategory(
                name=name,
                description=description or f"Suggested by vendor: {vendor.business_name}",
                is_active=False   # hidden from public dropdown until approved
            )
            db.add(new_category)
            db.flush()

            db.add(VendorCategoryMap(
                vendor_id=vendor.id,
                category_id=new_category.id
            ))
            db.commit()

            return {
                "message": "Category submitted for review. It will appear publicly once approved.",
                "category_id": new_category.id
            }
    

    def get_vendor_categories(self, db: Session, vendor_id: int):
        return (
            db.query(VendorCategory)
            .join(VendorCategoryMap, VendorCategoryMap.category_id == VendorCategory.id)
            .filter(VendorCategoryMap.vendor_id == vendor_id)
            .all()
        )


    def remove_category(self, db: Session, user_id: int, category_id: int):
        vendor = self.get_profile(db, user_id)

        mapping = db.query(VendorCategoryMap).filter(
            VendorCategoryMap.vendor_id == vendor.id,
            VendorCategoryMap.category_id == category_id
        ).first()

        if not mapping:
            raise HTTPException(status_code=404, detail="Category not assigned to this vendor")

        db.delete(mapping)
        db.commit()
        return {"message": "Category removed"}
    

    def add_document(self, db: Session, user_id: int, document_type: str, document_url: str):
        vendor = self.get_profile(db, user_id)

        document = VendorDocument(
            vendor_id=vendor.id,
            document_type=document_type,
            document_url=document_url,
            is_verified=False
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    def get_documents(self, db: Session, vendor_id: int):
        return db.query(VendorDocument).filter(
            VendorDocument.vendor_id == vendor_id
        ).all()

    def delete_document(self, db: Session, user_id: int, document_id: int):
        vendor = self.get_profile(db, user_id)

        document = db.query(VendorDocument).filter(
            VendorDocument.id == document_id,
            VendorDocument.vendor_id == vendor.id
        ).first()

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        db.delete(document)
        db.commit()
        return {"message": "Document deleted"}
    def get_compare_data(self, db: Session, vendor_ids: List[int]):
        if len(vendor_ids) < 2:
            raise HTTPException(status_code=400, detail="Select at least 2 vendors to compare")
        if len(vendor_ids) > 4:
            raise HTTPException(status_code=400, detail="You can compare up to 4 vendors at a time")

        vendors = db.query(VendorProfile).filter(
            VendorProfile.id.in_(vendor_ids), VendorProfile.is_approved == True
        ).all()

        if len(vendors) != len(set(vendor_ids)):
            raise HTTPException(status_code=404, detail="One or more selected vendors could not be found")

        vendor_map = {v.id: v for v in vendors}
        ordered_vendors = [vendor_map[vid] for vid in vendor_ids if vid in vendor_map]

        # Batch-fetch everything up front instead of per-vendor
        actual_ids = [v.id for v in ordered_vendors]

        all_services = db.query(VendorService).filter(
            VendorService.vendor_id.in_(actual_ids), VendorService.is_active == True
        ).all()
        services_by_vendor: dict = {}
        for s in all_services:
            services_by_vendor.setdefault(s.vendor_id, []).append(s)

        all_photos = db.query(VendorPhoto).filter(
            VendorPhoto.vendor_id.in_(actual_ids)
        ).order_by(VendorPhoto.sort_order.asc()).all()
        photos_by_vendor: dict = {}
        for p in all_photos:
            photos_by_vendor.setdefault(p.vendor_id, []).append(p)

        all_reviews = db.query(Review).filter(
            Review.vendor_id.in_(actual_ids)
        ).order_by(Review.created_at.desc()).all()
        reviews_by_vendor: dict = {}
        for r in all_reviews:
            reviews_by_vendor.setdefault(r.vendor_id, []).append(r)

        results = []
        for vendor in ordered_vendors:
            services = services_by_vendor.get(vendor.id, [])
            photos = photos_by_vendor.get(vendor.id, [])[:6]
            cover = next((p for p in photos if p.is_cover), photos[0] if photos else None)
            recent_reviews = reviews_by_vendor.get(vendor.id, [])[:2]
            prices = [float(s.price) for s in services]

            results.append({
                "id": vendor.id,
                "slug": vendor.slug,
                "business_name": vendor.business_name,
                "description": vendor.description,
                "address": vendor.address,
                "is_approved": vendor.is_approved,
                "avg_rating": vendor.avg_rating,
                "total_reviews": vendor.total_reviews,
                "total_bookings": vendor.total_bookings,
                "cover_photo_url": cover.photo_url if cover else None,
                "services": services,
                "photos": photos,
                "recent_reviews": recent_reviews,
                "min_price": min(prices) if prices else None,
                "max_price": max(prices) if prices else None,
            })

        return results
    def get_similar_vendors(self, db: Session, vendor_id: int, limit: int = 6):
        vendor = db.query(VendorProfile).filter(VendorProfile.id == vendor_id).first()
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")

        vendor_category_ids = [
            row.category_id for row in
            db.query(VendorCategoryMap.category_id).filter(VendorCategoryMap.vendor_id == vendor.id).all()
        ]

        base_query = db.query(VendorProfile).filter(
            VendorProfile.is_approved == True,
            VendorProfile.id != vendor.id
        )

        category_filtered_ids = None
        if vendor_category_ids:
            category_filtered_ids = db.query(VendorCategoryMap.vendor_id).filter(
                VendorCategoryMap.category_id.in_(vendor_category_ids)
            ).subquery()

        results = []
        seen_ids = set()

        # Tier 1: same category + same city
        if vendor.city_id and category_filtered_ids is not None:
            tier1 = base_query.filter(
                VendorProfile.city_id == vendor.city_id,
                VendorProfile.id.in_(category_filtered_ids)
            ).order_by(VendorProfile.rank_score.desc()).limit(limit).all()
            results.extend(tier1)
            seen_ids.update(v.id for v in tier1)

        # Tier 2: same category + same state (covers vendors with a city in the same state, or no city set at all)
        if len(results) < limit and category_filtered_ids is not None:
            city = db.query(City).filter(City.id == vendor.city_id).first() if vendor.city_id else None
            tier2_query = base_query.filter(VendorProfile.id.in_(category_filtered_ids), ~VendorProfile.id.in_(seen_ids))
            if city:
                city_ids_in_state = db.query(City.id).filter(City.state_id == city.state_id).subquery()
                tier2_query = tier2_query.filter(VendorProfile.city_id.in_(city_ids_in_state))
            tier2 = tier2_query.order_by(VendorProfile.rank_score.desc()).limit(limit - len(results)).all()
            results.extend(tier2)
            seen_ids.update(v.id for v in tier2)

        # Tier 3: same category, anywhere (covers the "state/city not found" case entirely —
        # ensures a photographer always sees other photographers even with no location data at all)
        if len(results) < limit and category_filtered_ids is not None:
            tier3 = base_query.filter(
                VendorProfile.id.in_(category_filtered_ids), ~VendorProfile.id.in_(seen_ids)
            ).order_by(VendorProfile.rank_score.desc()).limit(limit - len(results)).all()
            results.extend(tier3)
            seen_ids.update(v.id for v in tier3)

        # Tier 4: final fallback — any approved vendor at all, so the section is never empty
        # for a vendor with no categories/location set
        if len(results) < limit:
            tier4 = base_query.filter(~VendorProfile.id.in_(seen_ids)).order_by(
                VendorProfile.rank_score.desc()
            ).limit(limit - len(results)).all()
            results.extend(tier4)

        for v in results:
            cover = db.query(VendorPhoto).filter(VendorPhoto.vendor_id == v.id, VendorPhoto.is_cover == True).first()
            if not cover:
                cover = db.query(VendorPhoto).filter(VendorPhoto.vendor_id == v.id).order_by(VendorPhoto.sort_order.asc()).first()
            v.cover_photo_url = cover.photo_url if cover else None

        return results

    

    def get_nearby_vendors(
        self, db: Session,
        latitude: float, longitude: float,
        radius_km: float = 25,
        category_id: Optional[int] = None,
        skip: int = 0, limit: int = 20
    ):
        query = db.query(VendorProfile).filter(
            VendorProfile.is_approved == True,
            VendorProfile.latitude.isnot(None),
            VendorProfile.longitude.isnot(None)
        )

        if category_id:
            vendor_ids = db.query(VendorCategoryMap.vendor_id).filter(
                VendorCategoryMap.category_id == category_id
            ).subquery()
            query = query.filter(VendorProfile.id.in_(vendor_ids))

        candidates = query.all()

        results = []
        for vendor in candidates:
            distance = calculate_distance_km(latitude, longitude, vendor.latitude, vendor.longitude)
            if distance <= radius_km:
                cover = db.query(VendorPhoto).filter(VendorPhoto.vendor_id == vendor.id, VendorPhoto.is_cover == True).first()
                if not cover:
                    cover = db.query(VendorPhoto).filter(VendorPhoto.vendor_id == vendor.id).order_by(VendorPhoto.sort_order.asc()).first()
                vendor.cover_photo_url = cover.photo_url if cover else None

                all_services = db.query(VendorService).filter(
                    VendorService.vendor_id == vendor.id, VendorService.is_active == True
                ).order_by(VendorService.price.asc()).all()
                vendor.services_preview = all_services[:4]
                vendor.service_count = len(all_services)
                vendor.min_price = all_services[0].price if all_services else None
                vendor.distance_km = round(distance, 2)

                results.append(vendor)

        results.sort(key=lambda v: v.distance_km)
        return results[skip: skip + limit]
vendor_service = VendorService_()