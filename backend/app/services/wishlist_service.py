from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.customer import CustomerWishlist
from app.models.vendor import VendorProfile


class WishlistService_:

    def add_to_wishlist(self, db: Session, user_id: int, vendor_id: int):
        vendor = db.query(VendorProfile).filter(
            VendorProfile.id == vendor_id
        ).first()

        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")

        existing = db.query(CustomerWishlist).filter(
            CustomerWishlist.user_id == user_id,
            CustomerWishlist.vendor_id == vendor_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vendor already in your wishlist"
            )

        item = CustomerWishlist(user_id=user_id, vendor_id=vendor_id)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item


    def remove_from_wishlist(self, db: Session, user_id: int, vendor_id: int):
        item = db.query(CustomerWishlist).filter(
            CustomerWishlist.user_id == user_id,
            CustomerWishlist.vendor_id == vendor_id
        ).first()

        if not item:
            raise HTTPException(
                status_code=404,
                detail="This vendor is not in your wishlist"
            )

        db.delete(item)
        db.commit()
        return {"message": "Removed from wishlist"}


    def get_my_wishlist(self, db: Session, user_id: int):
        results = (
            db.query(CustomerWishlist, VendorProfile)
            .join(VendorProfile, CustomerWishlist.vendor_id == VendorProfile.id)
            .filter(CustomerWishlist.user_id == user_id)
            .order_by(CustomerWishlist.created_at.desc())
            .all()
        )

        return [
            {
                "wishlist_id": w.id,
                "vendor_id": v.id,
                "business_name": v.business_name,
                "description": v.description,
                "avg_rating": v.avg_rating,
                "total_reviews": v.total_reviews,
                "is_approved": v.is_approved,
                "saved_at": w.created_at
            }
            for w, v in results
        ]


    def check_is_wishlisted(self, db: Session, user_id: int, vendor_id: int) -> bool:
        return db.query(CustomerWishlist).filter(
            CustomerWishlist.user_id == user_id,
            CustomerWishlist.vendor_id == vendor_id
        ).first() is not None


wishlist_service = WishlistService_()