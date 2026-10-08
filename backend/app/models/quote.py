from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Quote(Base):
    __tablename__ = "quotes"

    id              = Column(Integer, primary_key=True, index=True)
    event_post_id   = Column(Integer, ForeignKey("event_posts.id"), nullable=True)  # nullable: can also quote directly from a vendor profile, no post involved
    vendor_id       = Column(Integer, ForeignKey("vendor_profiles.id"), nullable=False)
    customer_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id     = Column(Integer, ForeignKey("vendor_categories.id"), nullable=True)
    quoted_amount   = Column(Numeric(10, 2), nullable=False)
    message         = Column(Text, nullable=True)
    status          = Column(String(20), default="pending")  # pending / accepted / declined / withdrawn
    requested_by    = Column(String(20), nullable=False)      # "customer" (asked for a quote) or "vendor" (offered one unprompted)
    created_at      = Column(DateTime, default=datetime.utcnow)
    responded_at    = Column(DateTime, nullable=True)