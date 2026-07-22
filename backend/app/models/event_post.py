from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric, Boolean
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
    is_active      = Column(Boolean, default=True)
    created_at     = Column(DateTime, default=datetime.utcnow)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("User", foreign_keys=[customer_id])