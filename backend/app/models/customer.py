from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class CustomerProfile(Base):
    __tablename__ = "customer_profiles"

    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"), unique=True)
    city_id    = Column(Integer, ForeignKey("cities.id"))
    address    = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="customer_profile")


class CustomerWishlist(Base):
    __tablename__ = "customer_wishlist"

    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    vendor_id  = Column(Integer, ForeignKey("vendor_profiles.id"))
    created_at = Column(DateTime, default=datetime.utcnow)