from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class DataDeletionRequest(Base):
    __tablename__ = "data_deletion_requests"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_email   = Column(String(150), nullable=False)   # captured at request time, survives anonymization
    reason       = Column(Text, nullable=True)
    status       = Column(String(20), default="pending")  # pending / processed / rejected
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)   # admin who processed it


class DataExportRequest(Base):
    __tablename__ = "data_export_requests"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    status       = Column(String(20), default="pending")  # pending / ready / delivered
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)