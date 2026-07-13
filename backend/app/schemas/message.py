from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    receiver_id: int
    content: str
    booking_id: Optional[int] = None


class MessageResponse(BaseModel):
    id: int
    booking_id: Optional[int] = None
    sender_id: int
    receiver_id: int
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    conversation_key: str        # e.g. "vendor_12" or "booking_45" — uniquely identifies the thread
    booking_id: Optional[int] = None
    booking_ref: Optional[str] = None
    other_user_id: int
    other_user_name: str
    last_message: str
    last_message_at: datetime
    unread_count: int