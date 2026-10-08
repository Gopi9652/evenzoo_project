from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class EventPost(Base):
    __tablename__ = "event_posts"

    id             = Column(Integer, primary_key=True, index=True)
    customer_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    title          = Column(String(200), nullable=False)
    description    = Column(Text, nullable=False)
    event_location = Column(String(255), nullable=False)
    state_id       = Column(Integer, ForeignKey("states.id"), nullable=True)
    city_id        = Column(Integer, ForeignKey("cities.id"), nullable=True)
    budget_amount  = Column(Numeric(10, 2), nullable=True)
    event_date     = Column(DateTime, nullable=True)
    allow_messages = Column(Boolean, default=True) 
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime, default=datetime.utcnow)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category_id    = Column(Integer, ForeignKey("vendor_categories.id"), nullable=True)
    response_deadline = Column(DateTime, nullable=True)

    customer = relationship("User", foreign_keys=[customer_id])
    latitude  = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    place_id  = Column(String(255), nullable=True)
    service_radius_km = Column(Float, default=25)
    response_deadline = Column(DateTime, nullable=True)   # when the customer stops accepting new quotes