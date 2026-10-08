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
from app.models.booking import Booking, BookingService, EventType
from app.models.vendor import VendorService as VendorServiceModel
from app.services.engagement_service import engagement_service
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
        customer = db.query(User).filter(User.id == customer_id).first()
        service_names = ", ".join(s.name for s in selected_services) if selected_services else "no specific services"

        notification_service.create(
            db,
            user_id=vendor.user_id,
            title="New Booking Request",
            message=f"{customer.name if customer else 'A customer'} requested {service_names} on {data.event_date}.",
            type="booking",
            link=f"/vendor/bookings"
        )
        db.commit()
        db.refresh(booking)
        engagement_service.track(db, vendor.id, "booking_created", customer_id)
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
            customer = db.query(User).filter(User.id == customer_id).first()
            service_names = ", ".join(s.name for s in selected_services) if selected_services else "no specific services"

            notification_service.create(
                db,
                user_id=vendor.user_id,
                title="New Booking Request",
                message=f"{customer.name if customer else 'A customer'} requested {service_names} on {data.event_date}.",
                type="booking",
                link=f"/vendor/bookings"
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



    def _build_rich_booking(self, db: Session, booking: Booking, viewer_role: str) -> dict:
        """
        Builds a fully populated booking. Contact details are included only for
        the counterparty: a customer sees the vendor's phone, a vendor sees the
        customer's phone and email, and neither sees more than they need.
        """
        customer = db.query(User).filter(User.id == booking.customer_id).first()
        vendor_profile = db.query(VendorProfile).filter(VendorProfile.id == booking.vendor_id).first()
        vendor_owner = db.query(User).filter(User.id == vendor_profile.user_id).first() if vendor_profile else None
        event_type = db.query(EventType).filter(EventType.id == booking.event_type_id).first() if booking.event_type_id else None

        booked_items = db.query(BookingService).filter(BookingService.booking_id == booking.id).all()
        services = []
        for item in booked_items:
            svc = db.query(VendorServiceModel).filter(VendorServiceModel.id == item.service_id).first()
            services.append({
                "service_id": item.service_id,
                "name": svc.name if svc else "Service no longer available",
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total": item.total,
            })

        return {
            "id": booking.id,
            "booking_ref": booking.booking_ref,
            "status": booking.status,
            "event_date": booking.event_date,
            "event_time": booking.event_time,
            "event_location": booking.event_location,
            "guests_count": booking.guests_count,
            "special_requests": booking.special_requests,
            "total_amount": booking.total_amount,
            "platform_fee": booking.platform_fee,
            "vendor_amount": booking.vendor_amount,
            "event_type_name": event_type.name if event_type else None,
            "created_at": booking.created_at,
            "cancellation_reason": booking.cancellation_reason,
            "customer_id": booking.customer_id,
            "customer_name": customer.name if customer else "Customer",
            "customer_phone": customer.phone if (customer and viewer_role == "vendor") else None,
            "customer_email": customer.email if (customer and viewer_role == "vendor") else None,
            "vendor_id": booking.vendor_id,
            "vendor_user_id": vendor_profile.user_id if vendor_profile else 0,
            "vendor_business_name": vendor_profile.business_name if vendor_profile else "Vendor",
            "vendor_phone": vendor_owner.phone if (vendor_owner and viewer_role == "customer") else None,
            "services": services,
        }


    def get_customer_bookings_rich(self, db: Session, customer_id: int, status_filter: Optional[str] = None):
        query = db.query(Booking).filter(Booking.customer_id == customer_id)
        if status_filter:
            query = query.filter(Booking.status == status_filter)
        bookings = query.order_by(Booking.created_at.desc()).all()
        return [self._build_rich_booking(db, b, "customer") for b in bookings]


    def get_vendor_bookings_rich(self, db: Session, user_id: int, status_filter: Optional[str] = None):
        vendor = db.query(VendorProfile).filter(VendorProfile.user_id == user_id).first()
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor profile not found")

        query = db.query(Booking).filter(Booking.vendor_id == vendor.id)
        if status_filter:
            query = query.filter(Booking.status == status_filter)
        bookings = query.order_by(Booking.created_at.desc()).all()
        return [self._build_rich_booking(db, b, "vendor") for b in bookings]


    def get_booking_rich(self, db: Session, booking_id: int, user_id: int):
        booking = self.get_booking(db, booking_id, user_id)  # existing permission check
        vendor = db.query(VendorProfile).filter(VendorProfile.user_id == user_id).first()
        viewer_role = "vendor" if (vendor and booking.vendor_id == vendor.id) else "customer"
        return self._build_rich_booking(db, booking, viewer_role)


booking_service = BookingService_()