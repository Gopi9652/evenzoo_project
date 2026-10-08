from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime
from typing import List, Optional

class QuoteRequestCreate(BaseModel):
    """Customer asking a vendor for a price, either tied to a post or direct from a profile."""
    vendor_id: int
    event_post_id: Optional[int] = None
    category_id: Optional[int] = None
    message: Optional[str] = None


class QuoteOfferCreate(BaseModel):
    """Vendor sending a price in response (or proactively)."""
    quoted_amount: Decimal
    message: Optional[str] = None


class QuoteResponse(BaseModel):
    id: int
    event_post_id: Optional[int] = None
    vendor_id: int
    vendor_slug: Optional[str] = None
    vendor_business_name: Optional[str] = None
    vendor_avg_rating: Optional[Decimal] = None
    customer_id: int
    customer_name: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    quoted_amount: Optional[Decimal] = None
    message: Optional[str] = None
    status: str
    requested_by: str
    created_at: datetime
    responded_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class QuoteStatusUpdate(BaseModel):
    status: str  # accepted / declined / withdrawn


class BundleQuoteItem(BaseModel):
    category_id: int
    quoted_amount: Decimal


class BundleQuoteCreate(BaseModel):
    event_post_id: int
    items: List[BundleQuoteItem]
    message: Optional[str] = None

class QuotePostSummary(BaseModel):
    event_post_id: Optional[int] = None
    post_title: str
    event_date: Optional[datetime] = None
    is_expired: bool
    quote_count: int
    lowest_quote: Optional[float] = None
    highest_quote: Optional[float] = None