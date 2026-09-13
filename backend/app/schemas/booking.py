from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time, datetime
from decimal import Decimal

class VendorMiniResponse(BaseModel):
    id: int
    business_name: str

    class Config:
        from_attributes = True
# ── BOOKING ──
class BookingCreate(BaseModel):
    vendor_id:        int
    event_type_id:    int
    event_date:       date
    event_time:       Optional[time]  = None
    custom_event_type: Optional[str] = None 
    event_location:   str
    event_city_id:    Optional[int]   = None
    guests_count:     Optional[int]   = None
    special_requests: Optional[str]   = None
    service_ids:      List[int]       = []
    


class BookingStatusUpdate(BaseModel):
    status: str  # confirmed / cancelled / completed
    reason: Optional[str] = None


class BookingResponse(BaseModel):
    id:                 int
    booking_ref:        str
    customer_id:        int
    vendor_id:          int
    event_type_id:      Optional[int]     = None
    custom_event_type: Optional[str] = None 
    event_date:         date
    event_time:         Optional[time]    = None
    event_location:     str
    guests_count:       Optional[int]     = None
    special_requests:   Optional[str]     = None
    status:             str
    total_amount:       Decimal
    platform_fee:       Optional[Decimal] = None
    vendor_amount:      Optional[Decimal] = None
    cancellation_reason: Optional[str]   = None
    confirmed_at:       Optional[datetime] = None
    completed_at:       Optional[datetime] = None
    created_at:         datetime
    vendor:            Optional[VendorMiniResponse] = None
    
    class Config:
        from_attributes = True


class BookingListResponse(BaseModel):
    id:           int
    booking_ref:  str
    event_date:   date
    event_location: str
    status:       str
    total_amount: Decimal
    vendor_id:    int
    customer_id:  int
    created_at:   datetime
    vendor:            Optional[VendorMiniResponse] = None
    

    class Config:
        from_attributes = True


# ── EVENT TYPE ──
class EventTypeCreate(BaseModel):
    name: str

class EventTypeResponse(BaseModel):
    id:   int
    name: str

    class Config:
        from_attributes = True


# ── STATUS HISTORY ──
class StatusHistoryResponse(BaseModel):
    id:         int
    old_status: Optional[str] = None
    new_status: Optional[str] = None
    changed_by: Optional[int] = None
    reason:     Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
class AdminBookingDetailResponse(BaseModel):
    id:                  int
    booking_ref:         str
    customer_id:         int
    customer_name:       str
    customer_email:      str
    customer_phone:      str
    vendor_id:           int
    vendor_business_name: str
    vendor_owner_name:   str
    vendor_email:        str
    vendor_phone:        str
    event_date:          date
    event_location:      str
    status:              str
    total_amount:        Decimal
    platform_fee:        Optional[Decimal] = None
    vendor_amount:       Optional[Decimal] = None
    created_at:          datetime

    class Config:
        from_attributes = True