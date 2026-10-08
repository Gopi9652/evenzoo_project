from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class EventPostItemCreate(BaseModel):
    category_id: int
    budget_amount: Optional[Decimal] = None


class EventPostItemResponse(BaseModel):
    id: int
    category_id: int
    category_name: Optional[str] = None
    budget_amount: Optional[Decimal] = None

    class Config:
        from_attributes = True


class EventPostCreate(BaseModel):
    title:          str
    description:    str
    event_location: str
    state_id:       Optional[int]      = None
    city_id:        Optional[int]      = None
    category_id:    Optional[int]      = None   # kept for single-category posts (backward compatible)
    budget_amount:  Optional[Decimal]  = None
    event_date:     Optional[datetime] = None
    allow_messages: bool = True
    latitude:  Optional[float] = None
    longitude: Optional[float] = None
    place_id:  Optional[str]   = None
    items:          List[EventPostItemCreate] = []   # multi-event selection, each with its own budget


class EventPostUpdate(BaseModel):
    title:          Optional[str]       = None
    description:    Optional[str]       = None
    event_location: Optional[str]       = None
    state_id:       Optional[int]       = None
    city_id:        Optional[int]       = None
    category_id:    Optional[int]       = None
    budget_amount:  Optional[Decimal]   = None
    event_date:     Optional[datetime]  = None
    allow_messages: Optional[bool]      = None
    is_active:      Optional[bool]      = None
    latitude:  Optional[float] = None
    longitude: Optional[float] = None
    place_id:  Optional[str]   = None
    is_expired: bool = False
    items:          Optional[List[EventPostItemCreate]] = None


class EventPostResponse(BaseModel):
    id:             int
    customer_id:    int
    customer_name:  Optional[str] = None
    title:          str
    description:    str
    event_location: str
    state_id:       Optional[int]      = None
    city_id:        Optional[int]      = None
    category_id:    Optional[int]      = None
    category_name:  Optional[str]      = None
    budget_amount:  Optional[Decimal]  = None
    event_date:     Optional[datetime] = None
    allow_messages: bool = True
    is_active:      bool
    created_at:     datetime
    items:          List[EventPostItemResponse] = []
    quote_count:    int = 0
    is_expired: bool = False

    class Config:
        from_attributes = True