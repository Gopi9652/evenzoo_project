from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class VendorEngagementEvent(Base):
    """
    Lightweight funnel tracking. One row per meaningful interaction.
    event_type is one of: profile_view, enquiry (quote request or direct message initiated),
    conversation (first reply happens), quote_sent, shortlisted, booking_created.
    """
    __tablename__ = "vendor_engagement_events"

    id          = Column(Integer, primary_key=True, index=True)
    vendor_id   = Column(Integer, ForeignKey("vendor_profiles.id"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=True)   # null for anonymous/logged-out views
    event_type  = Column(String(30), nullable=False, index=True)
    created_at  = Column(DateTime, default=datetime.utcnow, index=True)