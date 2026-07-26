from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.review import Review
from app.models.booking import Booking
from app.models.vendor import VendorProfile
from app.schemas.review import ReviewCreate, ReviewReplyCreate
from app.services.notification_service import notification_service
from app.utils.vendor_scoring import calculate_rank_score

class ReviewService_:

    # ── CREATE REVIEW ──
    def create_review(
        self, db: Session,
        customer_id: int,
        data: ReviewCreate
    ):
        booking = db.query(Booking).filter(
            Booking.id          == data.booking_id,
            Booking.customer_id == customer_id
        ).first()

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )

        if booking.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only review completed bookings"
            )

        existing = db.query(Review).filter(
            Review.booking_id == booking.id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review already submitted for this booking"
            )

        overall = round(
            (data.quality_rating + data.price_rating + data.service_rating) / 3,
            2
        )

        review = Review(
            booking_id=booking.id,
            customer_id=customer_id,
            vendor_id=booking.vendor_id,
            quality_rating=data.quality_rating,
            price_rating=data.price_rating,
            service_rating=data.service_rating,
            overall_rating=overall,
            title=data.title,
            body=data.body,
            is_verified=True
        )
        db.add(review)

        # Recalculate vendor's average rating
        self._recalculate_vendor_rating(db, booking.vendor_id)

        # Notify vendor
        vendor = db.query(VendorProfile).filter(
            VendorProfile.id == booking.vendor_id
        ).first()

        notification_service.create(
            db,
            user_id=vendor.user_id,
            title="New Review Received",
            message=f"You received a {overall}★ review for booking {booking.booking_ref}",
            type="review",
            link=f"/vendor/reviews/{review.id}"
        )

        db.commit()
        db.refresh(review)
        return review


    # ── VENDOR REPLY TO REVIEW ──
    def reply_to_review(
        self, db: Session,
        user_id: int,
        review_id: int,
        data: ReviewReplyCreate
    ):
        review = db.query(Review).filter(
            Review.id == review_id
        ).first()

        if not review:
            raise HTTPException(
                status_code=404,
                detail="Review not found"
            )

        vendor = db.query(VendorProfile).filter(
            VendorProfile.user_id == user_id,
            VendorProfile.id      == review.vendor_id
        ).first()

        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only reply to your own reviews"
            )

        review.vendor_reply    = data.vendor_reply
        review.vendor_reply_at = datetime.utcnow()

        db.commit()
        db.refresh(review)
        return review


    # ── GET VENDOR REVIEWS ──
    def get_vendor_reviews(
        self, db: Session,
        vendor_id: int
    ):
        return db.query(Review).filter(
            Review.vendor_id == vendor_id
        ).order_by(Review.created_at.desc()).all()


    # ── RECALCULATE VENDOR AVG RATING ──
    def _recalculate_vendor_rating(
        self, db: Session,
        vendor_id: int
    ):
        reviews = db.query(Review).filter(
            Review.vendor_id == vendor_id
        ).all()

        vendor = db.query(VendorProfile).filter(
            VendorProfile.id == vendor_id
        ).first()

        if not reviews:
            vendor.avg_rating    = 0
            vendor.total_reviews = 0
            return

        total = sum(float(r.overall_rating) for r in reviews)
        avg   = round(total / len(reviews), 2)

        vendor.avg_rating    = avg
        vendor.total_reviews = len(reviews)

        # Update rank score — simple formula combining rating + bookings
        vendor.rank_score = calculate_rank_score(avg, vendor.total_bookings)

    def update_review(
        self, db: Session,
        customer_id: int,
        review_id: int,
        data
    ):
        review = db.query(Review).filter(
            Review.id == review_id,
            Review.customer_id == customer_id
        ).first()

        if not review:
            raise HTTPException(
                status_code=404,
                detail="Review not found or you don't have permission to edit it"
            )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(review, field, value)

        # Recalculate overall_rating if any rating field changed
        if any(k in update_data for k in ["quality_rating", "price_rating", "service_rating"]):
            review.overall_rating = round(
                (review.quality_rating + review.price_rating + review.service_rating) / 3, 2
            )

        db.commit()

        # Vendor rating must reflect the edit
        self._recalculate_vendor_rating(db, review.vendor_id)

        db.commit()
        db.refresh(review)
        return review


    def delete_review(
        self, db: Session,
        customer_id: int,
        review_id: int
    ):
        review = db.query(Review).filter(
            Review.id == review_id,
            Review.customer_id == customer_id
        ).first()

        if not review:
            raise HTTPException(
                status_code=404,
                detail="Review not found or you don't have permission to delete it"
            )

        vendor_id = review.vendor_id
        db.delete(review)
        db.commit()

        # Vendor rating must reflect the removal
        self._recalculate_vendor_rating(db, vendor_id)
        db.commit()

        return {"message": "Review deleted successfully"}
    
    def get_my_reviews(self, db: Session, customer_id: int):
        return db.query(Review).filter(
            Review.customer_id == customer_id
        ).order_by(Review.created_at.desc()).all()

review_service = ReviewService_()