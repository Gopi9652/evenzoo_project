from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, nullable=False, index=True)
    phone         = Column(String(15), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    role          = Column(String(20), nullable=False)
    is_active     = Column(Boolean, default=True)
    is_verified   = Column(Boolean, default=False)
    profile_photo = Column(String(500))
    deletion_requested_at = Column(DateTime, nullable=True)
    deleted_at             = Column(DateTime, nullable=True)
    pending_email  = Column(String(150), nullable=True)   # ← new
    pending_phone  = Column(String(15), nullable=True)    # ← new
    created_at    = Column(DateTime, default=datetime.utcnow)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    vendor_profile   = relationship("VendorProfile", back_populates="user", uselist=False)
    customer_profile = relationship("CustomerProfile", back_populates="user", uselist=False)
    bookings_made    = relationship("Booking", foreign_keys="Booking.customer_id", back_populates="customer")
    notifications    = relationship("Notification", back_populates="user")
    reviews          = relationship("Review", foreign_keys="Review.customer_id", back_populates="customer")

class OTPVerification(Base):
    __tablename__ = "otp_verifications"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, nullable=False)
    otp_code   = Column(String(6), nullable=False)
    purpose    = Column(String(30))
    expires_at = Column(DateTime, nullable=False)
    is_used    = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)






class PasswordReset(Base):
    __tablename__ = "password_resets"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, nullable=False)
    token      = Column(Text, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used    = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, nullable=False)
    token      = Column(Text, unique=True, nullable=False)
    device_info = Column(String(255), nullable=True)
    ip_address  = Column(String(45), nullable=True)
    last_used_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)