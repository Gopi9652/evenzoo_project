from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationResponse(BaseModel):
    id:         int
    title:      str
    message:    str
    type:       Optional[str] = None
    is_read:    bool
    link:       Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UnreadCountResponse(BaseModel):
    unread_count: int