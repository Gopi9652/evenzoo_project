from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime

from app.models.user import User
from app.models.data_request import DataDeletionRequest, DataExportRequest
from app.models.booking import Booking
from app.models.review import Review
from app.models.event_post import EventPost
from app.models.message import Message
from app.models.notification import Notification
from app.models.vendor import VendorProfile
from app.models.customer import CustomerProfile
from app.schemas.privacy import DeletionRequestCreate


class PrivacyService_:

    # ── ACCOUNT DELETION ──

    def request_deletion(self, db: Session, user_id: int, data: DeletionRequestCreate):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Prevent duplicate pending requests
        existing = db.query(DataDeletionRequest).filter(
            DataDeletionRequest.user_id == user_id,
            DataDeletionRequest.status == "pending"
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A deletion request is already pending for this account"
            )

        request = DataDeletionRequest(
            user_id=user_id,
            user_email=user.email,
            reason=data.reason
        )
        db.add(request)

        user.deletion_requested_at = datetime.utcnow()
        user.is_active = False  # immediately suspend login while the request is processed

        db.commit()
        db.refresh(request)
        return request


    def get_my_deletion_requests(self, db: Session, user_id: int):
        return db.query(DataDeletionRequest).filter(
            DataDeletionRequest.user_id == user_id
        ).order_by(DataDeletionRequest.requested_at.desc()).all()


    def cancel_deletion_request(self, db: Session, user_id: int, request_id: int):
        request = db.query(DataDeletionRequest).filter(
            DataDeletionRequest.id == request_id,
            DataDeletionRequest.user_id == user_id,
            DataDeletionRequest.status == "pending"
        ).first()

        if not request:
            raise HTTPException(status_code=404, detail="Pending request not found")

        request.status = "cancelled"

        user = db.query(User).filter(User.id == user_id).first()
        user.deletion_requested_at = None
        user.is_active = True

        db.commit()
        return {"message": "Deletion request cancelled. Your account is active again."}


    # ── ADMIN: PROCESS DELETION ──

    def get_pending_deletion_requests(self, db: Session):
        return db.query(DataDeletionRequest).filter(
            DataDeletionRequest.status == "pending"
        ).order_by(DataDeletionRequest.requested_at.asc()).all()


    def process_deletion(self, db: Session, admin_id: int, request_id: int):
        """
        Anonymizes the user's personal data rather than hard-deleting the row.
        This preserves referential integrity for bookings/reviews/payments
        (which legally may need to be retained for accounting/tax purposes)
        while removing personally identifying information.
        """
        request = db.query(DataDeletionRequest).filter(
            DataDeletionRequest.id == request_id,
            DataDeletionRequest.status == "pending"
        ).first()

        if not request:
            raise HTTPException(status_code=404, detail="Pending request not found")

        user = db.query(User).filter(User.id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        anon_tag = f"deleted_user_{user.id}"

        user.name = "Deleted User"
        user.email = f"{anon_tag}@deleted.evenzoo.in"
        user.phone = f"0000000{user.id}"[-10:]
        user.profile_photo = None
        user.is_active = False
        user.deleted_at = datetime.utcnow()

        # Anonymize linked profile records too
        vendor_profile = db.query(VendorProfile).filter(VendorProfile.user_id == user.id).first()
        if vendor_profile:
            vendor_profile.business_name = "Deleted Vendor"
            vendor_profile.description = None
            vendor_profile.address = None
            vendor_profile.gstin = None
            vendor_profile.pan_number = None
            vendor_profile.bank_account = None
            vendor_profile.bank_ifsc = None
            vendor_profile.bank_name = None

        # Anonymize message content sent by this user
        db.query(Message).filter(Message.sender_id == user.id).update({
            "content": "[Message deleted by user request]"
        })

        request.status = "processed"
        request.processed_at = datetime.utcnow()
        request.processed_by = admin_id

        db.commit()
        return {"message": f"Account for request #{request_id} has been anonymized and deactivated"}


    def reject_deletion(self, db: Session, admin_id: int, request_id: int, reason: str):
        request = db.query(DataDeletionRequest).filter(
            DataDeletionRequest.id == request_id,
            DataDeletionRequest.status == "pending"
        ).first()

        if not request:
            raise HTTPException(status_code=404, detail="Pending request not found")

        request.status = "rejected"
        request.processed_at = datetime.utcnow()
        request.processed_by = admin_id

        user = db.query(User).filter(User.id == request.user_id).first()
        user.is_active = True
        user.deletion_requested_at = None

        db.commit()
        return {"message": "Deletion request rejected, account reactivated", "reason": reason}


    # ── DATA EXPORT (right to access) ──

    def export_my_data(self, db: Session, user_id: int) -> dict:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        bookings = db.query(Booking).filter(Booking.customer_id == user_id).all()
        reviews = db.query(Review).filter(Review.customer_id == user_id).all()
        event_posts = db.query(EventPost).filter(EventPost.customer_id == user_id).all()
        messages_sent = db.query(Message).filter(Message.sender_id == user_id).count()
        messages_received = db.query(Message).filter(Message.receiver_id == user_id).count()
        notifications_count = db.query(Notification).filter(Notification.user_id == user_id).count()

        profile = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

        vendor_profile = db.query(VendorProfile).filter(VendorProfile.user_id == user_id).first()
        if vendor_profile:
            profile["vendor_business_name"] = vendor_profile.business_name
            profile["vendor_city_id"] = vendor_profile.city_id

        return {
            "profile": profile,
            "bookings": [
                {
                    "id": b.id,
                    "booking_ref": b.booking_ref,
                    "event_date": b.event_date.isoformat() if b.event_date else None,
                    "status": b.status,
                    "total_amount": float(b.total_amount) if b.total_amount else None,
                }
                for b in bookings
            ],
            "reviews_given": [
                {
                    "id": r.id,
                    "overall_rating": float(r.overall_rating) if r.overall_rating else None,
                    "body": r.body,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in reviews
            ],
            "event_posts": [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in event_posts
            ],
            "messages_sent": messages_sent,
            "messages_received": messages_received,
            "notifications_count": notifications_count,
        }


privacy_service = PrivacyService_()