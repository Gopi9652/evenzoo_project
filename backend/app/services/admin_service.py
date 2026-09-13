from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from datetime import datetime

from app.models.user import User
from app.models.vendor import VendorProfile
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.review import Review
from app.models.notification import PlatformSetting
from app.schemas.admin import VendorApprovalRequest, PlatformSettingUpdate
from app.services.notification_service import notification_service


class AdminService_:

    # ── GET PENDING VENDOR APPROVALS ──
    def get_pending_vendors(self, db: Session):
        return db.query(VendorProfile).filter(
            VendorProfile.is_approved == False,
            VendorProfile.rejection_reason.is_(None)
        ).order_by(VendorProfile.created_at.asc()).all()


    # ── APPROVE / REJECT VENDOR ──
    def review_vendor(
        self, db: Session,
        vendor_id: int,
        data: VendorApprovalRequest
    ):
        vendor = db.query(VendorProfile).filter(
            VendorProfile.id == vendor_id
        ).first()

        if not vendor:
            raise HTTPException(
                status_code=404,
                detail="Vendor not found"
            )

        vendor.is_approved = data.is_approved

        if data.is_approved:
            vendor.approval_date    = datetime.utcnow()
            vendor.rejection_reason = None

            notification_service.create(
                db,
                user_id=vendor.user_id,
                title="Vendor Profile Approved! 🎉",
                message="Your business is now live on Evenzoo. Customers can find and book you now.",
                type="system",
                link="/vendor/dashboard"
            )
        else:
            vendor.rejection_reason = data.rejection_reason

            notification_service.create(
                db,
                user_id=vendor.user_id,
                title="Vendor Profile Needs Changes",
                message=f"Your profile was not approved. Reason: {data.rejection_reason}",
                type="system",
                link="/vendor/profile"
            )

        db.commit()
        db.refresh(vendor)
        return vendor


    # ── GET ALL VENDORS (with filter) ──
    def get_all_vendors(
        self, db: Session,
        approved_only: bool = None
    ):
        query = db.query(VendorProfile)

        if approved_only is not None:
            query = query.filter(
                VendorProfile.is_approved == approved_only
            )

        return query.order_by(
            VendorProfile.created_at.desc()
        ).all()


    # ── GET ALL BOOKINGS (admin overview) ──
    def get_all_bookings(
        self, db: Session,
        status_filter: str = None
    ):
        query = db.query(Booking)

        if status_filter:
            query = query.filter(Booking.status == status_filter)

        bookings = query.order_by(Booking.created_at.desc()).limit(100).all()

        results = []
        for booking in bookings:
            customer = db.query(User).filter(User.id == booking.customer_id).first()
            vendor_profile = db.query(VendorProfile).filter(VendorProfile.id == booking.vendor_id).first()
            vendor_owner = db.query(User).filter(User.id == vendor_profile.user_id).first() if vendor_profile else None

            results.append({
                "id": booking.id,
                "booking_ref": booking.booking_ref,
                "customer_id": booking.customer_id,
                "customer_name": customer.name if customer else "Unknown",
                "customer_email": customer.email if customer else "Unknown",
                "customer_phone": customer.phone if customer else "Unknown",
                "vendor_id": booking.vendor_id,
                "vendor_business_name": vendor_profile.business_name if vendor_profile else "Unknown",
                "vendor_owner_name": vendor_owner.name if vendor_owner else "Unknown",
                "vendor_email": vendor_owner.email if vendor_owner else "Unknown",
                "vendor_phone": vendor_owner.phone if vendor_owner else "Unknown",
                "event_date": booking.event_date,
                "event_location": booking.event_location,
                "status": booking.status,
                "total_amount": booking.total_amount,
                "platform_fee": booking.platform_fee,
                "vendor_amount": booking.vendor_amount,
                "created_at": booking.created_at,
            })

        return results


    # ── PLATFORM STATS DASHBOARD ──
    def get_platform_stats(self, db: Session):
        total_users     = db.query(User).count()
        total_customers = db.query(User).filter(
            User.role == "customer"
        ).count()
        total_vendors = db.query(User).filter(
            User.role == "vendor"
        ).count()
        total_approved_vendors = db.query(VendorProfile).filter(
            VendorProfile.is_approved == True
        ).count()
        pending_approvals = db.query(VendorProfile).filter(
            VendorProfile.is_approved == False,
            VendorProfile.rejection_reason.is_(None)
        ).count()

        total_bookings = db.query(Booking).count()
        pending_bookings = db.query(Booking).filter(
            Booking.status == "pending"
        ).count()
        confirmed_bookings = db.query(Booking).filter(
            Booking.status == "confirmed"
        ).count()
        completed_bookings = db.query(Booking).filter(
            Booking.status == "completed"
        ).count()
        cancelled_bookings = db.query(Booking).filter(
            Booking.status == "cancelled"
        ).count()

        revenue_result = db.query(
            func.coalesce(func.sum(Payment.amount), 0)
        ).filter(Payment.status == "captured").scalar()

        commission_result = db.query(
            func.coalesce(func.sum(Booking.platform_fee), 0)
        ).join(Payment, Payment.booking_id == Booking.id).filter(
            Payment.status == "captured"
        ).scalar()

        total_reviews = db.query(Review).count()

        avg_rating_result = db.query(
            func.avg(VendorProfile.avg_rating)
        ).filter(VendorProfile.total_reviews > 0).scalar()

        return {
            "total_users":              total_users,
            "total_customers":          total_customers,
            "total_vendors":            total_vendors,
            "total_approved_vendors":   total_approved_vendors,
            "pending_vendor_approvals": pending_approvals,
            "total_bookings":           total_bookings,
            "pending_bookings":         pending_bookings,
            "confirmed_bookings":       confirmed_bookings,
            "completed_bookings":       completed_bookings,
            "cancelled_bookings":       cancelled_bookings,
            "total_revenue":            revenue_result or 0,
            "total_platform_commission": commission_result or 0,
            "total_reviews":            total_reviews,
            "avg_platform_rating":      round(avg_rating_result, 2) if avg_rating_result else None
        }


    # ── FORCE CANCEL BOOKING (dispute resolution) ──
    def force_cancel_booking(
        self, db: Session,
        booking_id: int,
        reason: str
    ):
        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()

        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        if booking.status in ["completed", "cancelled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel a {booking.status} booking"
            )

        booking.status              = "cancelled"
        booking.cancelled_at        = datetime.utcnow()
        booking.cancellation_reason = reason
        booking.cancelled_by        = "admin"

        # Reverse any pending vendor payout tied to this booking
        from app.models.payment import VendorPayout
        payout = db.query(VendorPayout).filter(
            VendorPayout.booking_id == booking.id,
            VendorPayout.status == "pending"
        ).first()

        if payout:
            payout.status = "cancelled"

        vendor = db.query(VendorProfile).filter(
            VendorProfile.id == booking.vendor_id
        ).first()

        notification_service.create(
            db, user_id=booking.customer_id,
            title="Booking Cancelled by Admin",
            message=f"Your booking {booking.booking_ref} was cancelled. Reason: {reason}",
            type="system"
        )
        notification_service.create(
            db, user_id=vendor.user_id,
            title="Booking Cancelled by Admin",
            message=f"Booking {booking.booking_ref} was cancelled. Reason: {reason}. Any pending payout for this booking has been cancelled.",
            type="system"
        )

        db.commit()
        db.refresh(booking)
        return booking
    # ── PLATFORM SETTINGS ──
    def get_setting(self, db: Session, key: str):
        setting = db.query(PlatformSetting).filter(
            PlatformSetting.key == key
        ).first()

        if not setting:
            raise HTTPException(
                status_code=404,
                detail="Setting not found"
            )
        return setting


    def get_all_settings(self, db: Session):
        return db.query(PlatformSetting).all()


    def update_setting(
        self, db: Session,
        key: str,
        data: PlatformSettingUpdate
    ):
        setting = db.query(PlatformSetting).filter(
            PlatformSetting.key == key
        ).first()

        if not setting:
            setting = PlatformSetting(
                key=key,
                value=data.value
            )
            db.add(setting)
        else:
            setting.value = data.value

        db.commit()
        db.refresh(setting)
        return setting


    # ── SUSPEND / ACTIVATE USER ──
    def toggle_user_status(
        self, db: Session,
        user_id: int,
        is_active: bool
    ):
        user = db.query(User).filter(
            User.id == user_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        user.is_active = is_active
        db.commit()
        db.refresh(user)

        action = "activated" if is_active else "suspended"
        return {"message": f"User {action} successfully"}
    
    def find_duplicate_vendors(self, db: Session):
            """
            Flags potential duplicate vendor accounts based on:
            - Same phone number pattern (different digit, common typo)
            - Same business name (case-insensitive, fuzzy)
            - Same bank account number across different vendor profiles
            """
            from sqlalchemy import func

            vendors = db.query(VendorProfile).join(User).all()

            duplicates = []
            seen_names = {}
            seen_bank_accounts = {}

            for v in vendors:
                normalized_name = v.business_name.strip().lower().replace(" ", "")

                # Same business name check
                if normalized_name in seen_names:
                    duplicates.append({
                        "type": "similar_business_name",
                        "vendor_1_id": seen_names[normalized_name],
                        "vendor_2_id": v.id,
                        "detail": f"Both use business name similar to '{v.business_name}'"
                    })
                else:
                    seen_names[normalized_name] = v.id

                # Same bank account check (most reliable duplicate signal)
                if v.bank_account:
                    if v.bank_account in seen_bank_accounts:
                        duplicates.append({
                            "type": "same_bank_account",
                            "vendor_1_id": seen_bank_accounts[v.bank_account],
                            "vendor_2_id": v.id,
                            "detail": "Both vendor profiles use the same bank account number"
                        })
                    else:
                        seen_bank_accounts[v.bank_account] = v.id

            return duplicates
    def get_all_users(self, db: Session, role_filter: str = None, active_only: bool = None):
            query = db.query(User)

            if role_filter:
                query = query.filter(User.role == role_filter)

            if active_only is not None:
                query = query.filter(User.is_active == active_only)

            return query.order_by(User.created_at.desc()).limit(200).all()

    def get_booking_detail(self, db: Session, booking_id: int):
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        customer = db.query(User).filter(User.id == booking.customer_id).first()
        vendor_profile = db.query(VendorProfile).filter(VendorProfile.id == booking.vendor_id).first()
        vendor_owner = db.query(User).filter(User.id == vendor_profile.user_id).first() if vendor_profile else None

        history = db.query(BookingStatusHistory).filter(
            BookingStatusHistory.booking_id == booking_id
        ).order_by(BookingStatusHistory.created_at.asc()).all()

        payment = db.query(Payment).filter(Payment.booking_id == booking_id).first()

        return {
            "booking": {
                "id": booking.id,
                "booking_ref": booking.booking_ref,
                "event_date": booking.event_date,
                "event_location": booking.event_location,
                "guests_count": booking.guests_count,
                "special_requests": booking.special_requests,
                "status": booking.status,
                "total_amount": booking.total_amount,
                "platform_fee": booking.platform_fee,
                "vendor_amount": booking.vendor_amount,
                "created_at": booking.created_at,
            },
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
            } if customer else None,
            "vendor": {
                "id": vendor_profile.id,
                "business_name": vendor_profile.business_name,
                "owner_name": vendor_owner.name if vendor_owner else None,
                "email": vendor_owner.email if vendor_owner else None,
                "phone": vendor_owner.phone if vendor_owner else None,
            } if vendor_profile else None,
            "payment": {
                "status": payment.status,
                "amount": payment.amount,
                "paid_at": payment.paid_at,
            } if payment else None,
            "history": [
                {
                    "old_status": h.old_status,
                    "new_status": h.new_status,
                    "reason": h.reason,
                    "created_at": h.created_at,
                }
                for h in history
            ]
        }
admin_service = AdminService_()