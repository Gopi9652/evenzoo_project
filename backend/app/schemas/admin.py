from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class VendorApprovalRequest(BaseModel):
    is_approved:      bool
    rejection_reason: Optional[str] = None


class PlatformStatsResponse(BaseModel):
    total_users:            int
    total_customers:        int
    total_vendors:          int
    total_approved_vendors: int
    pending_vendor_approvals: int
    total_bookings:          int
    pending_bookings:        int
    confirmed_bookings:      int
    completed_bookings:      int
    cancelled_bookings:      int
    total_revenue:           Decimal
    total_platform_commission: Decimal
    total_reviews:            int
    avg_platform_rating:      Optional[Decimal] = None


class PlatformSettingUpdate(BaseModel):
    value: str


class PlatformSettingResponse(BaseModel):
    key:         str
    value:       str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True