from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.middleware.auth_middleware import (
    get_current_user, get_customer, get_vendor
)
from app.models.user import User
from app.services.booking_service import booking_service
from app.schemas.booking import (
    BookingCreate, BookingResponse,
    BookingListResponse, BookingStatusUpdate,
    EventTypeResponse, StatusHistoryResponse
)

router = APIRouter(tags=["Bookings"])


# ── EVENT TYPES (public) ──
@router.get("/event-types", response_model=List[EventTypeResponse])
def get_event_types(db: Session = Depends(get_db)):
    return booking_service.get_event_types(db)


@router.post("/event-types/seed")
def seed_event_types(db: Session = Depends(get_db)):
    return booking_service.seed_event_types(db)


# ── CUSTOMER ROUTES ──
@router.post("", response_model=BookingResponse)
def create_booking(
    data: BookingCreate,
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return booking_service.create_booking(
        db, current_user.id, data
    )


@router.get("/my", response_model=List[BookingListResponse])
def get_my_bookings(
    status: Optional[str] = Query(None),
    current_user: User    = Depends(get_current_user),
    db: Session           = Depends(get_db)
):
    return booking_service.get_customer_bookings(
        db, current_user.id, status
    )


# ── VENDOR ROUTES ──
@router.get("/vendor", response_model=List[BookingListResponse])
def get_vendor_bookings(
    status: Optional[str] = Query(None),
    current_user: User    = Depends(get_vendor),
    db: Session           = Depends(get_db)
):
    return booking_service.get_vendor_bookings(
        db, current_user.id, status
    )


# ── SHARED ROUTES ──
@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id:   int,
    current_user: User    = Depends(get_current_user),
    db: Session           = Depends(get_db)
):
    return booking_service.get_booking(
        db, booking_id, current_user.id
    )


@router.put("/{booking_id}/status",
            response_model=BookingResponse)
def update_booking_status(
    booking_id:   int,
    data:         BookingStatusUpdate,
    current_user: User    = Depends(get_current_user),
    db: Session           = Depends(get_db)
):
    return booking_service.update_status(
        db, booking_id, current_user.id, data
    )


@router.get("/{booking_id}/history",
            response_model=List[StatusHistoryResponse])
def get_booking_history(
    booking_id:   int,
    current_user: User    = Depends(get_current_user),
    db: Session           = Depends(get_db)
):
    return booking_service.get_booking_history(db, booking_id)