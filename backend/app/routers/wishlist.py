from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.middleware.auth_middleware import get_customer
from app.models.user import User
from app.services.wishlist_service import wishlist_service
from app.schemas.wishlist import (
    WishlistAddRequest, WishlistItemResponse, WishlistVendorResponse
)

router = APIRouter(tags=["Wishlist"])


@router.post("", response_model=WishlistItemResponse)
def add_to_wishlist(
    data: WishlistAddRequest,
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return wishlist_service.add_to_wishlist(db, current_user.id, data.vendor_id)


@router.delete("/{vendor_id}")
def remove_from_wishlist(
    vendor_id: int,
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return wishlist_service.remove_from_wishlist(db, current_user.id, vendor_id)


@router.get("", response_model=List[WishlistVendorResponse])
def get_my_wishlist(
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return wishlist_service.get_my_wishlist(db, current_user.id)


@router.get("/check/{vendor_id}")
def check_wishlisted(
    vendor_id: int,
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    is_saved = wishlist_service.check_is_wishlisted(db, current_user.id, vendor_id)
    return {"is_wishlisted": is_saved}