from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal


class CompareServiceItem(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    price_type: str

    class Config:
        from_attributes = True


class ComparePhotoItem(BaseModel):
    id: int
    photo_url: str
    is_cover: bool

    class Config:
        from_attributes = True


class CompareReviewSnippet(BaseModel):
    id: int
    overall_rating: Optional[Decimal] = None
    title: Optional[str] = None
    body: Optional[str] = None

    class Config:
        from_attributes = True


class VendorCompareData(BaseModel):
    id:               int
    business_name:    str
    description:      Optional[str] = None
    address:          Optional[str] = None
    is_approved:      bool
    avg_rating:       Optional[Decimal] = None
    total_reviews:    int
    total_bookings:   int
    cover_photo_url:  Optional[str] = None
    services:         List[CompareServiceItem] = []
    photos:           List[ComparePhotoItem] = []
    recent_reviews:   List[CompareReviewSnippet] = []
    min_price:        Optional[Decimal] = None
    max_price:        Optional[Decimal] = None

    class Config:
        from_attributes = True