from sqlalchemy import (Column, Integer, String, DateTime,
                        Numeric, ForeignKey, Text)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id                  = Column(Integer, primary_key=True, index=True)
    booking_id          = Column(Integer, ForeignKey("bookings.id"))
    razorpay_order_id   = Column(String(100), unique=True)
    razorpay_payment_id = Column(String(100), unique=True)
    razorpay_signature  = Column(String(300))
    amount              = Column(Numeric(10, 2), nullable=False)
    currency            = Column(String(5), default="INR")
    status              = Column(String(20), default="pending")
    payment_method      = Column(String(50))
    paid_at             = Column(DateTime)
    created_at          = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking", back_populates="payment")


class Refund(Base):
    __tablename__ = "refunds"

    id                 = Column(Integer, primary_key=True)
    payment_id         = Column(Integer, ForeignKey("payments.id"))
    razorpay_refund_id = Column(String(100), unique=True)
    amount             = Column(Numeric(10, 2), nullable=False)
    reason             = Column(Text)
    status             = Column(String(20), default="pending")
    initiated_by       = Column(Integer, ForeignKey("users.id"))
    processed_at       = Column(DateTime)
    created_at         = Column(DateTime, default=datetime.utcnow)


class VendorPayout(Base):
    __tablename__ = "vendor_payouts"

    id           = Column(Integer, primary_key=True)
    vendor_id    = Column(Integer, ForeignKey("vendor_profiles.id"))
    booking_id   = Column(Integer, ForeignKey("bookings.id"))
    amount       = Column(Numeric(10, 2), nullable=False)
    status       = Column(String(20), default="pending")
    payout_ref   = Column(String(100))
    processed_at = Column(DateTime)
    created_at   = Column(DateTime, default=datetime.utcnow)