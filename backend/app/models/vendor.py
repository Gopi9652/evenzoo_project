from sqlalchemy import (Column, Integer, String, Boolean,
                        DateTime, Text, Numeric, Date,
                        Time, ForeignKey)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from sqlalchemy import UniqueConstraint

class VendorProfile(Base):
    __tablename__ = "vendor_profiles"

    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id"), unique=True)
    business_name    = Column(String(200), nullable=False)
    description      = Column(Text)
    city_id          = Column(Integer, ForeignKey("cities.id"))
    address          = Column(Text)
    profile_photo_url = Column(String(500), nullable=True)
    gstin            = Column(String(20))
    pan_number       = Column(String(20))
    bank_account     = Column(String(30))
    bank_ifsc        = Column(String(20))
    bank_name        = Column(String(100))
    is_approved      = Column(Boolean, default=False)
    approval_date    = Column(DateTime)
    rejection_reason = Column(Text)
    avg_rating       = Column(Numeric(3, 2), default=0.00)
    total_reviews    = Column(Integer, default=0)
    total_bookings   = Column(Integer, default=0)
    rank_score       = Column(Numeric(5, 2), default=0.00)
    created_at       = Column(DateTime, default=datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.utcnow,
                              onupdate=datetime.utcnow)
    
    show_whatsapp = Column(Boolean, default=False)
    user         = relationship("User", back_populates="vendor_profile")
    services     = relationship("VendorService", back_populates="vendor")
    photos       = relationship("VendorPhoto", back_populates="vendor")
    documents    = relationship("VendorDocument", back_populates="vendor")
    availability = relationship("VendorAvailability", back_populates="vendor")
    bookings     = relationship("Booking", foreign_keys="Booking.vendor_id",
                                back_populates="vendor")
    reviews      = relationship("Review", foreign_keys="Review.vendor_id",
                                back_populates="vendor")


class VendorCategory(Base):
    __tablename__ = "vendor_categories"

    id          = Column(Integer, primary_key=True)
    name        = Column(String(100), nullable=False)
    description = Column(Text)
    icon        = Column(String(100))
    is_active   = Column(Boolean, default=True)


class VendorCategoryMap(Base):
    __tablename__ = "vendor_category_map"

    id          = Column(Integer, primary_key=True)
    vendor_id   = Column(Integer, ForeignKey("vendor_profiles.id"))
    category_id = Column(Integer, ForeignKey("vendor_categories.id"))


class VendorService(Base):
    __tablename__ = "vendor_services"

    id           = Column(Integer, primary_key=True)
    vendor_id    = Column(Integer, ForeignKey("vendor_profiles.id"))
    name         = Column(String(200), nullable=False)
    description  = Column(Text)
    price        = Column(Numeric(10, 2), nullable=False)
    price_type   = Column(String(20))
    min_quantity = Column(Integer, default=1)
    max_quantity = Column(Integer)
    is_active    = Column(Boolean, default=True)
    created_at   = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("VendorProfile", back_populates="services")


class VendorPhoto(Base):
    __tablename__ = "vendor_photos"

    id         = Column(Integer, primary_key=True)
    vendor_id  = Column(Integer, ForeignKey("vendor_profiles.id"))
    photo_url  = Column(String(500), nullable=False)
    caption    = Column(String(200))
    is_cover   = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("VendorProfile", back_populates="photos")


class VendorDocument(Base):
    __tablename__ = "vendor_documents"

    id            = Column(Integer, primary_key=True)
    vendor_id     = Column(Integer, ForeignKey("vendor_profiles.id"))
    document_type = Column(String(50))
    document_url  = Column(String(500), nullable=False)
    is_verified   = Column(Boolean, default=False)
    created_at    = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("VendorProfile", back_populates="documents")




class VendorAvailability(Base):
    __tablename__ = "vendor_availability"

    id           = Column(Integer, primary_key=True)
    vendor_id    = Column(Integer, ForeignKey("vendor_profiles.id"))
    date         = Column(Date, nullable=False)
    is_available = Column(Boolean, default=True)
    reason       = Column(String(200))

    vendor = relationship("VendorProfile", back_populates="availability")

    __table_args__ = (
        UniqueConstraint('vendor_id', 'date', name='uq_vendor_availability_date'),
    )


class VendorWorkingHours(Base):
    __tablename__ = "vendor_working_hours"

    id          = Column(Integer, primary_key=True)
    vendor_id   = Column(Integer, ForeignKey("vendor_profiles.id"))
    day_of_week = Column(Integer, nullable=False)
    open_time   = Column(Time)
    close_time  = Column(Time)
    is_off_day  = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint('vendor_id', 'day_of_week', name='uq_vendor_working_hours_day'),
    )