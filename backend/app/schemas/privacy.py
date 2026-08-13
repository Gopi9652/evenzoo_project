from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DeletionRequestCreate(BaseModel):
    reason: Optional[str] = None


class DeletionRequestResponse(BaseModel):
    id: int
    status: str
    requested_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ExportRequestResponse(BaseModel):
    id: int
    status: str
    requested_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserDataExport(BaseModel):
    """The actual bundle of a user's personal data, returned as JSON."""
    profile: dict
    bookings: list
    reviews_given: list
    event_posts: list
    messages_sent: int
    messages_received: int
    notifications_count: int