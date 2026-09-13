from datetime import date, time, datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    Numeric,
    Date,
    Time,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.database import Base

# ── VENDOR PROFILE ──
class VendorProfileCreate(BaseModel):
    business_name: str
    description:   Optional[str] = None
    city_id:       Optional[int] = None
    address:       Optional[str] = None
    gstin:         Optional[str] = None
    pan_number:    Optional[str] = None
    bank_account:  Optional[str] = None
    bank_ifsc:     Optional[str] = None
    bank_name:     Optional[str] = None


class VendorProfileUpdate(BaseModel):
    business_name: Optional[str] = None
    description:   Optional[str] = None
    city_id:       Optional[int] = None
    address:       Optional[str] = None
    gstin:         Optional[str] = None
    pan_number:    Optional[str] = None
    bank_account:  Optional[str] = None
    bank_ifsc:     Optional[str] = None
    bank_name:     Optional[str] = None


class VendorProfileResponse(BaseModel):
    id:               int
    user_id:          int
    business_name:    str
    description:      Optional[str] = None
    city_id:          Optional[int] = None
    address:          Optional[str] = None
    is_approved:      bool
    avg_rating:       Optional[Decimal] = None
    total_reviews:    int
    total_bookings:   int
    profile_photo_url: Optional[str] = None
    whatsapp_number:  Optional[str] = True 

    class Config:
        from_attributes = True


# ── VENDOR SERVICE ──
class VendorServiceCreate(BaseModel):
    name:         str
    description:  Optional[str] = None
    price:        Decimal
    price_type:   str  # fixed / per_hour / per_day / per_person
    min_quantity: Optional[int] = 1
    max_quantity: Optional[int] = None


class VendorServiceUpdate(BaseModel):
    name:         Optional[str]     = None
    description:  Optional[str]     = None
    price:        Optional[Decimal] = None
    price_type:   Optional[str]     = None
    min_quantity: Optional[int]     = None
    max_quantity: Optional[int]     = None
    is_active:    Optional[bool]    = None


class VendorServiceResponse(BaseModel):
    id:           int
    vendor_id:    int
    name:         str
    description:  Optional[str]     = None
    price:        Decimal
    price_type:   str
    min_quantity: int
    max_quantity: Optional[int]     = None
    is_active:    bool

    class Config:
        from_attributes = True


# ── VENDOR PHOTO ──
class VendorPhotoCreate(BaseModel):
    photo_url:  str
    caption:    Optional[str] = None
    is_cover:   bool = False
    sort_order: int  = 0


class VendorPhotoResponse(BaseModel):
    id:         int
    vendor_id:  int
    photo_url:  str
    caption:    Optional[str] = None
    is_cover:   bool
    sort_order: int

    class Config:
        from_attributes = True


# ── VENDOR AVAILABILITY ──
class VendorAvailabilityCreate(BaseModel):
    date:         date
    is_available: bool = True
    reason:       Optional[str] = None


class VendorAvailabilityResponse(BaseModel):
    id:           int
    vendor_id:    int
    date:         date
    is_available: bool
    reason:       Optional[str] = None

    class Config:
        from_attributes = True


# ── VENDOR WORKING HOURS ──
class WorkingHoursCreate(BaseModel):
    day_of_week: int  # 0=Mon 6=Sun
    open_time:   Optional[time] = None
    close_time:  Optional[time] = None
    is_off_day:  bool = False


class WorkingHoursResponse(BaseModel):
    id:          int
    vendor_id:   int
    day_of_week: int
    open_time:   Optional[time] = None
    close_time:  Optional[time] = None
    is_off_day:  bool

    class Config:
        from_attributes = True


# ── VENDOR LIST (for customer browsing) ──
class VendorListResponse(BaseModel):
    id:            int
    business_name: str
    description:   Optional[str]    = None
    avg_rating:    Optional[Decimal] = None
    total_reviews: int
    total_bookings: int
    city_id:       Optional[int]    = None
    is_approved:   bool
    profile_photo_url: Optional[str] = None

    class Config:
        from_attributes = True


# ── CATEGORY ──
class CategoryResponse(BaseModel):
    id:          int
    name:        str
    description: Optional[str] = None
    icon:        Optional[str] = None

    class Config:
        from_attributes = True

class CustomCategoryRequest(BaseModel):
    name: str
    description: Optional[str] = None


class VendorDocumentResponse(BaseModel):
    id: int
    vendor_id: int
    document_type: str
    document_url: str
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

