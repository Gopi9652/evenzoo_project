from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional

from app.models.booking import (
    Booking, BookingService,
    BookingStatusHistory, EventType
)
from app.models.vendor import (
    VendorProfile, VendorService, VendorAvailability
)
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingStatusUpdate
from app.utils.booking_ref import generate_booking_ref
from app.config import settings
from app.services.notification_service import notification_service
from app.utils.vendor_scoring import calculate_rank_score
class BookingService_:

    # ── CREATE BOOKING ──
    def create_booking(
        self, db: Session,
        customer_id: int,
        data: BookingCreate
    ):
        # Check vendor exists and is approved
        vendor = db.query(VendorProfile).filter(
            VendorProfile.id          == data.vendor_id,
            VendorProfile.is_approved == True
        ).first()

        if not vendor:
            raise HTTPException(
                status_code=404,
                detail="Vendor not found or not approved"
            )
        
        # Validate event type — must have either a known type OR a custom one
        if not data.event_type_id and not data.custom_event_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please select an event type or specify a custom one"
            )

        if data.event_type_id:
            event_type_exists = db.query(EventType).filter(
                EventType.id == data.event_type_id
            ).first()
            if not event_type_exists:
                raise HTTPException(
                    status_code=404,
                    detail="Selected event type not found"
                )

        # Check vendor availability on that date
        blocked = db.query(VendorAvailability).filter(
            VendorAvailability.vendor_id    == data.vendor_id,
            VendorAvailability.date         == data.event_date,
            VendorAvailability.is_available == False
        ).first()

        if blocked:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vendor is not available on this date"
            )

        # Check no existing confirmed booking same date
        existing = db.query(Booking).filter(
            Booking.vendor_id   == data.vendor_id,
            Booking.event_date  == data.event_date,
            Booking.status.in_(["pending", "confirmed"])
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vendor already has a booking on this date"
            )

        # Calculate total from selected services
        total_amount = 0
        selected_services = []

        if data.service_ids:
            for sid in data.service_ids:
                service = db.query(VendorService).filter(
                    VendorService.id        == sid,
                    VendorService.vendor_id == data.vendor_id,
                    VendorService.is_active == True
                ).first()

                if not service:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Service {sid} not found"
                    )

                total_amount += float(service.price)
                selected_services.append(service)

        # Calculate platform fee and vendor amount
        platform_fee  = round(total_amount * settings.PLATFORM_COMMISSION, 2)
        vendor_amount = round(total_amount - platform_fee, 2)

        # Generate unique booking reference
        booking_ref = generate_booking_ref()
        while db.query(Booking).filter(
            Booking.booking_ref == booking_ref
        ).first():
            booking_ref = generate_booking_ref()

        # Create booking
        booking = Booking(
            booking_ref=booking_ref,
            customer_id=customer_id,
            vendor_id=data.vendor_id,
            event_type_id=data.event_type_id,
            custom_event_type=data.custom_event_type,
            event_date=data.event_date,
            event_time=data.event_time,
            event_location=data.event_location,
            event_city_id=data.event_city_id,
            guests_count=data.guests_count,
            special_requests=data.special_requests,
            status="pending",
            total_amount=total_amount,
            platform_fee=platform_fee,
            vendor_amount=vendor_amount
        )
        db.add(booking)
        db.flush()

        # Add booking services
        for service in selected_services:
            db.add(BookingService(
                booking_id=booking.id,
                service_id=service.id,
                quantity=1,
                unit_price=service.price,
                total=service.price
            ))

        # Add status history
        db.add(BookingStatusHistory(
            booking_id=booking.id,
            old_status=None,
            new_status="pending",
            changed_by=customer_id,
            reason="Booking created"
        ))

        # Update vendor booking count
        vendor.total_bookings += 1

        # Keep rank_score fresh even when no new review has come in
        #vendor.rank_score = calculate_rank_score(avg, vendor.total_bookings)
        # Notify vendor of new booking
        notification_service.create(
            db,
            user_id=vendor.user_id,
            title="New Booking Request",
            message=f"You have a new booking request for {data.event_date}",
            type="booking",
            link=f"/vendor/bookings/{booking.id}"
        )
        db.commit()
        db.refresh(booking)
        return booking


    # ── GET BOOKING BY ID ──
    def get_booking(
        self, db: Session,
        booking_id: int,
        user_id: int
    ):
        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )

        # Check access — only customer or vendor of this booking
        vendor = db.query(VendorProfile).filter(
            VendorProfile.user_id == user_id
        ).first()

        is_customer = booking.customer_id == user_id
        is_vendor   = vendor and booking.vendor_id == vendor.id

        if not is_customer and not is_vendor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return booking


    # ── GET CUSTOMER BOOKINGS ──
    def get_customer_bookings(
        self,
        db: Session,
        customer_id: int,
        status_filter: Optional[str] = None
    ):
        query = db.query(Booking).filter(
            Booking.customer_id == customer_id
        )

        if status_filter:
            query = query.filter(Booking.status == status_filter)

        bookings = query.order_by(Booking.created_at.desc()).all()

        for booking in bookings:
            print(booking.vendor.business_name)

        return bookings


    # ── GET VENDOR BOOKINGS ──
    def get_vendor_bookings(
        self, db: Session,
        user_id: int,
        status_filter: Optional[str] = None
    ):
        vendor = db.query(VendorProfile).filter(
            VendorProfile.user_id == user_id
        ).first()

        if not vendor:
            raise HTTPException(
                status_code=404,
                detail="Vendor profile not found"
            )

        query = db.query(Booking).filter(
            Booking.vendor_id == vendor.id
        )

        if status_filter:
            query = query.filter(Booking.status == status_filter)

        return query.order_by(Booking.created_at.desc()).all()


    # ── UPDATE BOOKING STATUS ──
    def update_status(
        self, db: Session,
        booking_id: int,
        user_id: int,
        data: BookingStatusUpdate
    ):
        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )

        # Valid transitions
        valid_transitions = {
            "pending":   ["confirmed", "cancelled"],
            "confirmed": ["completed", "cancelled"],
            "completed": [],
            "cancelled": []
        }

        if data.status not in valid_transitions.get(booking.status, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot move from {booking.status} to {data.status}"
            )

        old_status     = booking.status
        booking.status = data.status

        # Set timestamps
        if data.status == "confirmed":
            booking.confirmed_at = datetime.utcnow()

        if data.status == "completed":
            booking.completed_at = datetime.utcnow()

        if data.status == "cancelled":
            booking.cancelled_at        = datetime.utcnow()
            booking.cancellation_reason = data.reason
            booking.cancelled_by        = "vendor" if self._is_vendor(
                db, user_id, booking.vendor_id
            ) else "customer"

        # Add status history
        db.add(BookingStatusHistory(
            booking_id=booking.id,
            old_status=old_status,
            new_status=data.status,
            changed_by=user_id,
            reason=data.reason
        ))
        # Notify customer of status change
        notify_user_id = booking.customer_id
        status_messages = {
            "confirmed": "Your booking has been confirmed!",
            "cancelled": f"Your booking was cancelled. Reason: {data.reason or 'Not specified'}",
            "completed": "Your event is marked as completed. Please leave a review!"
        }

        if data.status in status_messages:
            notification_service.create(
                db,
                user_id=notify_user_id,
                title=f"Booking {data.status.capitalize()}",
                message=status_messages[data.status],
                type="booking",
                link=f"/bookings/{booking.id}"
            )
        db.commit()
        db.refresh(booking)
        return booking


    # ── GET BOOKING HISTORY ──
    def get_booking_history(
        self, db: Session,
        booking_id: int
    ):
        return db.query(BookingStatusHistory).filter(
            BookingStatusHistory.booking_id == booking_id
        ).order_by(BookingStatusHistory.created_at.asc()).all()


    # ── HELPER ──
    def _is_vendor(
        self, db: Session,
        user_id: int,
        vendor_id: int
    ) -> bool:
        vendor = db.query(VendorProfile).filter(
            VendorProfile.user_id == user_id,
            VendorProfile.id      == vendor_id
        ).first()
        return vendor is not None


    # ── GET EVENT TYPES ──
    def get_event_types(self, db: Session):
        return db.query(EventType).all()


    # ── SEED EVENT TYPES ──
    def seed_event_types(self, db: Session):
        types = [
            "Wedding", "Reception", "Birthday Party",
            "Engagement", "Baby Shower", "Corporate Event",
            "Graduation", "Anniversary", "Festival", "Other"
        ]
        for name in types:
            exists = db.query(EventType).filter(
                EventType.name == name
            ).first()
            if not exists:
                db.add(EventType(name=name))
        db.commit()
        return {"message": "Event types seeded"}


booking_service = BookingService_()