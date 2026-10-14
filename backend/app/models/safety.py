from sqlalchemy import (Column, Integer, String, DateTime,
                        Date, Time, Text, Numeric, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class UserBlock(Base):
    __tablename__ = "user_blocks"
    id = Column(Integer, primary_key=True)
    blocker_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    blocked_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("blocker_id", "blocked_id"),)

class UserReport(Base):
    __tablename__ = "user_reports"
    id = Column(Integer, primary_key=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reported_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reason = Column(String(50), nullable=False)
    details = Column(Text)
    status = Column(String(20), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)