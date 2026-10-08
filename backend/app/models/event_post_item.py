from sqlalchemy import Column, Integer, Numeric, ForeignKey
from app.database import Base


class EventPostItem(Base):
    __tablename__ = "event_post_items"

    id            = Column(Integer, primary_key=True, index=True)
    event_post_id = Column(Integer, ForeignKey("event_posts.id"), nullable=False)
    category_id   = Column(Integer, ForeignKey("vendor_categories.id"), nullable=False)
    budget_amount = Column(Numeric(10, 2), nullable=True)