from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional

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
    def update_profile(
        self, db: Session,
        user_id: int,
        data: VendorProfileUpdate
    ):
        vendor = self.get_profile(db, user_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vendor, field, value)

        db.commit()
        db.refresh(vendor)
        return vendor


    def list_vendors(
        self, db: Session,
        state_id:    Optional[int] = None,
        city_id:     Optional[int] = None,
        category_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ):
        query = db.query(VendorProfile).filter(
            VendorProfile.is_approved == True
        )

        if state_id:
            city_ids_in_state = db.query(City.id).filter(City.state_id == state_id).subquery()
            query = query.filter(VendorProfile.city_id.in_(city_ids_in_state))

        if city_id:
            query = query.filter(VendorProfile.city_id == city_id)

        if category_id:
            vendor_ids = db.query(VendorCategoryMap.vendor_id).filter(
                VendorCategoryMap.category_id == category_id
            ).subquery()
            query = query.filter(VendorProfile.id.in_(vendor_ids))

        query = query.order_by(VendorProfile.rank_score.desc())

        return query.offset(skip).limit(limit).all()
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
        """
        Returns full comparison data for up to 4 vendors in a single call —
        services, photos, recent reviews, and min/max pricing — so the
        frontend can render a side-by-side comparison without needing
        a separate round-trip per vendor.
        """
        if len(vendor_ids) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Select at least 2 vendors to compare"
            )

        if len(vendor_ids) > 4:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You can compare up to 4 vendors at a time"
            )

        vendors = db.query(VendorProfile).filter(
            VendorProfile.id.in_(vendor_ids),
            VendorProfile.is_approved == True
        ).all()

        if len(vendors) != len(set(vendor_ids)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more selected vendors could not be found"
            )

        # Preserve the order the customer selected them in, not arbitrary DB order
        vendor_map = {v.id: v for v in vendors}
        ordered_vendors = [vendor_map[vid] for vid in vendor_ids if vid in vendor_map]

        results = []
        for vendor in ordered_vendors:
            services = db.query(VendorService).filter(
                VendorService.vendor_id == vendor.id,
                VendorService.is_active == True
            ).all()

            photos = db.query(VendorPhoto).filter(
                VendorPhoto.vendor_id == vendor.id
            ).order_by(VendorPhoto.sort_order.asc()).limit(6).all()

            cover = next((p for p in photos if p.is_cover), photos[0] if photos else None)

            recent_reviews = db.query(Review).filter(
                Review.vendor_id == vendor.id
            ).order_by(Review.created_at.desc()).limit(2).all()

            prices = [float(s.price) for s in services]

            results.append({
                "id": vendor.id,
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
vendor_service = VendorService_()