from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ReviewCreate(BaseModel):
    booking_id:     int
    quality_rating: int = Field(ge=1, le=5)
    price_rating:   int = Field(ge=1, le=5)
    service_rating: int = Field(ge=1, le=5)
    title:          Optional[str] = None
    body:           Optional[str] = None


class ReviewReplyCreate(BaseModel):
    vendor_reply: str


class ReviewResponse(BaseModel):
    id:              int
    booking_id:      int
    customer_id:     int
    vendor_id:       int
    quality_rating:  int
    price_rating:    int
    service_rating:  int
    overall_rating:  Optional[Decimal] = None
    title:           Optional[str]     = None
    body:            Optional[str]     = None
    is_verified:     bool
    vendor_reply:    Optional[str]     = None
    vendor_reply_at: Optional[datetime] = None
    created_at:      datetime

    class Config:
        from_attributes = True

class ReviewUpdate(BaseModel):
    quality_rating: Optional[int] = Field(None, ge=1, le=5)
    price_rating: Optional[int] = Field(None, ge=1, le=5)
    service_rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = None
    body: Optional[str] = None