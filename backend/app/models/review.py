from sqlalchemy import (Column, Integer, String, DateTime,
                        Numeric, ForeignKey, Text, Boolean)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id              = Column(Integer, primary_key=True, index=True)
    booking_id      = Column(Integer, ForeignKey("bookings.id"), unique=True)
    customer_id     = Column(Integer, ForeignKey("users.id"))
    vendor_id       = Column(Integer, ForeignKey("vendor_profiles.id"))
    quality_rating  = Column(Integer)
    price_rating    = Column(Integer)
    service_rating  = Column(Integer)
    overall_rating  = Column(Numeric(3, 2))
    title           = Column(String(200))
    body            = Column(Text)
    is_verified     = Column(Boolean, default=True)
    vendor_reply    = Column(Text)
    vendor_reply_at = Column(DateTime)
    created_at      = Column(DateTime, default=datetime.utcnow)

    booking  = relationship("Booking", back_populates="review")
    customer = relationship("User", foreign_keys=[customer_id],
                            back_populates="reviews")
    vendor   = relationship("VendorProfile", foreign_keys=[vendor_id],
                            back_populates="reviews")