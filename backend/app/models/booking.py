from sqlalchemy import (Column, Integer, String, DateTime,
                        Date, Time, Text, Numeric, ForeignKey)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class EventType(Base):
    __tablename__ = "event_types"

    id   = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)


class Booking(Base):
    __tablename__ = "bookings"

    id                  = Column(Integer, primary_key=True, index=True)
    booking_ref         = Column(String(20), unique=True, nullable=False)
    customer_id         = Column(Integer, ForeignKey("users.id"))
    vendor_id           = Column(Integer, ForeignKey("vendor_profiles.id"))
    event_type_id       = Column(Integer, ForeignKey("event_types.id"))
    custom_event_type   = Column(String(100), nullable=True)
    event_date          = Column(Date, nullable=False)
    event_time          = Column(Time)
    event_location      = Column(Text, nullable=False)
    event_city_id       = Column(Integer, ForeignKey("cities.id"))
    guests_count        = Column(Integer)
    special_requests    = Column(Text)
    status              = Column(String(20), default="pending")
    total_amount        = Column(Numeric(10, 2), nullable=False)
    platform_fee        = Column(Numeric(10, 2))
    vendor_amount       = Column(Numeric(10, 2))
    cancellation_reason = Column(Text)
    cancelled_by        = Column(String(20))
    cancelled_at        = Column(DateTime)
    confirmed_at        = Column(DateTime)
    completed_at        = Column(DateTime)
    created_at          = Column(DateTime, default=datetime.utcnow)
    updated_at          = Column(DateTime, default=datetime.utcnow,
                                 onupdate=datetime.utcnow)

    customer = relationship("User", foreign_keys=[customer_id],
                            back_populates="bookings_made")
    vendor   = relationship("VendorProfile", foreign_keys=[vendor_id],
                            back_populates="bookings")
    services = relationship("BookingService", back_populates="booking")
    history  = relationship("BookingStatusHistory", back_populates="booking")
    payment  = relationship("Payment", back_populates="booking", uselist=False)
    review   = relationship("Review", back_populates="booking", uselist=False)


class BookingService(Base):
    __tablename__ = "booking_services"

    id         = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    service_id = Column(Integer, ForeignKey("vendor_services.id"))
    quantity   = Column(Integer, default=1)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total      = Column(Numeric(10, 2), nullable=False)

    booking = relationship("Booking", back_populates="services")


class BookingStatusHistory(Base):
    __tablename__ = "booking_status_history"

    id         = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    old_status = Column(String(20))
    new_status = Column(String(20))
    changed_by = Column(Integer, ForeignKey("users.id"))
    reason     = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking", back_populates="history")