from sqlalchemy import (Column, Integer, String, Boolean,
                        DateTime, Text, ForeignKey)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    title      = Column(String(200), nullable=False)
    message    = Column(Text, nullable=False)
    type       = Column(String(50))
    is_read    = Column(Boolean, default=False)
    link       = Column(String(300))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="notifications")


class EmailLog(Base):
    __tablename__ = "email_logs"

    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    to_email   = Column(String(150), nullable=False)
    subject    = Column(String(300), nullable=False)
    template   = Column(String(100))
    status     = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)


class PlatformSetting(Base):
    __tablename__ = "platform_settings"

    id          = Column(Integer, primary_key=True)
    key         = Column(String(100), unique=True, nullable=False)
    value       = Column(Text, nullable=False)
    description = Column(String(300))
    updated_at  = Column(DateTime, default=datetime.utcnow,
                         onupdate=datetime.utcnow)