from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal


class WishlistAddRequest(BaseModel):
    vendor_id: int


class WishlistItemResponse(BaseModel):
    id: int
    vendor_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WishlistVendorResponse(BaseModel):
    """Wishlist item joined with vendor details, for the 'My Saved Vendors' page"""
    wishlist_id: int
    vendor_id: int
    business_name: str
    description: Optional[str] = None
    avg_rating: Optional[Decimal] = None
    total_reviews: int
    is_approved: bool
    saved_at: datetime