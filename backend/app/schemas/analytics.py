from pydantic import BaseModel
from typing import List, Dict


class MonthlyBooking(BaseModel):
    month: int
    year: int
    count: int


class MonthlyRevenue(BaseModel):
    month: int
    year: int
    revenue: float


class VendorAnalyticsResponse(BaseModel):
    vendor_id: int
    business_name: str
    total_bookings: int
    completion_rate: float
    cancellation_rate: float
    total_earnings: float
    avg_rating: float
    total_reviews: int
    monthly_bookings: List[MonthlyBooking]
    monthly_revenue: List[MonthlyRevenue]
    status_breakdown: Dict[str, int]
    rating_distribution: Dict[int, int]