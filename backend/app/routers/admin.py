from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.middleware.auth_middleware import get_admin
from app.models.user import User
from app.services.admin_service import admin_service
from app.schemas.admin import (
    VendorApprovalRequest, PlatformStatsResponse,
    PlatformSettingUpdate, PlatformSettingResponse, UserListResponse
)
from app.schemas.vendor import VendorProfileResponse
from app.schemas.booking import BookingListResponse
from app.models.booking import EventType
from app.models.vendor import VendorCategory
router = APIRouter(tags=["Admin"])


# ── VENDOR APPROVALS ──
@router.get("/vendors/pending",
            response_model=List[VendorProfileResponse])
def get_pending_vendors(
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return admin_service.get_pending_vendors(db)


@router.get("/vendors", response_model=List[VendorProfileResponse])
def get_all_vendors(
    approved_only: Optional[bool] = Query(None),
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return admin_service.get_all_vendors(db, approved_only)


@router.put("/vendors/{vendor_id}/review",
            response_model=VendorProfileResponse)
def review_vendor(
    vendor_id: int,
    data: VendorApprovalRequest,
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return admin_service.review_vendor(db, vendor_id, data)


# ── BOOKINGS OVERVIEW ──
@router.get("/bookings", response_model=List[BookingListResponse])
def get_all_bookings(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return admin_service.get_all_bookings(db, status)


@router.put("/bookings/{booking_id}/force-cancel")
def force_cancel_booking(
    booking_id: int,
    reason: str,
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return admin_service.force_cancel_booking(db, booking_id, reason)


# ── PLATFORM STATS ──
@router.get("/stats", response_model=PlatformStatsResponse)
def get_platform_stats(
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return admin_service.get_platform_stats(db)


# ── PLATFORM SETTINGS ──
@router.get("/settings", response_model=List[PlatformSettingResponse])
def get_all_settings(
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return admin_service.get_all_settings(db)


@router.put("/settings/{key}", response_model=PlatformSettingResponse)
def update_setting(
    key: str,
    data: PlatformSettingUpdate,
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return admin_service.update_setting(db, key, data)


# ── USER MANAGEMENT ──
@router.put("/users/{user_id}/status")
def toggle_user_status(
    user_id: int,
    is_active: bool,
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return admin_service.toggle_user_status(db, user_id, is_active)

@router.post("/event-types")
def add_event_type(
    name: str,
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(EventType).filter(EventType.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Event type already exists")

    new_type = EventType(name=name)
    db.add(new_type)
    db.commit()
    db.refresh(new_type)
    return new_type
@router.get("/categories/pending")
def get_pending_categories(
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return db.query(VendorCategory).filter(
        VendorCategory.is_active == False
    ).all()


@router.put("/categories/{category_id}/approve")
def approve_category(
    category_id: int,
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    category = db.query(VendorCategory).filter(
        VendorCategory.id == category_id
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.is_active = True
    db.commit()
    return {"message": "Category approved and now publicly visible"}

@router.get("/vendors/duplicates")
def get_duplicate_vendors(
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return admin_service.find_duplicate_vendors(db)


@router.get("/users", response_model=List[UserListResponse])
def get_all_users(
    role: Optional[str] = Query(None),
    active_only: Optional[bool] = Query(None),
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return admin_service.get_all_users(db, role, active_only)



@router.get("/vendors/directory", response_model=List[VendorProfileResponse])
def get_vendor_directory(
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    """Full vendor directory with photos for admin browsing."""
    return db.query(VendorProfile).order_by(VendorProfile.business_name).all()