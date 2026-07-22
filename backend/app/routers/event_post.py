from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, get_customer, get_vendor
from app.models.user import User
from app.models.vendor import VendorProfile
from app.services.event_post_service import event_post_service
from app.schemas.event_post import EventPostCreate, EventPostUpdate, EventPostResponse

router = APIRouter(tags=["Event Posts"])


# ── CUSTOMER ROUTES ──

@router.post("", response_model=EventPostResponse)
def create_post(
    data: EventPostCreate,
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return event_post_service.create_post(db, current_user.id, data)


@router.get("/my", response_model=List[EventPostResponse])
def get_my_posts(
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return event_post_service.get_my_posts(db, current_user.id)


@router.put("/{post_id}", response_model=EventPostResponse)
def update_post(
    post_id: int,
    data: EventPostUpdate,
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return event_post_service.update_post(db, current_user.id, post_id, data)


@router.delete("/{post_id}")
def delete_post(
    post_id: int,
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return event_post_service.delete_post(db, current_user.id, post_id)


# ── VENDOR ROUTES ──

@router.get("/vendor-feed", response_model=List[EventPostResponse])
def get_posts_for_vendor(
    filter_state_id: Optional[int] = Query(None),
    filter_city_id:  Optional[int] = Query(None),
    skip:  int = Query(0),
    limit: int = Query(20),
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    vendor = db.query(VendorProfile).filter(
        VendorProfile.user_id == current_user.id
    ).first()

    vendor_city_id = vendor.city_id if vendor else None
    vendor_state_id = None
    if vendor and vendor.city_id:
        from app.models.location import City
        city = db.query(City).filter(City.id == vendor.city_id).first()
        vendor_state_id = city.state_id if city else None

    return event_post_service.list_posts_for_vendor(
        db, vendor_state_id, vendor_city_id,
        filter_state_id, filter_city_id, skip, limit
    )


# ── SHARED ──

@router.get("/{post_id}", response_model=EventPostResponse)
def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    return event_post_service.get_post_by_id(db, post_id)