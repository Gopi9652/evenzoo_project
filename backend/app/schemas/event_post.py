from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class EventPostCreate(BaseModel):
    title:          str
    description:    str
    event_location: str
    state_id:       Optional[int]      = None
    city_id:        Optional[int]      = None
    budget_amount:  Optional[Decimal]  = None
    event_date:     Optional[datetime] = None
    category_id:    Optional[int]      = None 


class EventPostUpdate(BaseModel):
    title:          Optional[str]       = None
    description:    Optional[str]       = None
    event_location: Optional[str]       = None
    state_id:       Optional[int]       = None
    city_id:        Optional[int]       = None
    budget_amount:  Optional[Decimal]   = None
    event_date:     Optional[datetime]  = None
    is_active:      Optional[bool]      = None
    category_id:    Optional[int]      = None 


class EventPostResponse(BaseModel):
    id:             int
    customer_id:    int
    customer_name:  Optional[str] = None   # populated manually, not a real column
    title:          str
    description:    str
    event_location: str
    state_id:       Optional[int]      = None
    city_id:        Optional[int]      = None
    budget_amount:  Optional[Decimal]  = None
    event_date:     Optional[datetime] = None
    is_active:      bool
    created_at:     datetime
    category_id:    Optional[int]      = None  
    category_name:  Optional[str]      = None

    class Config:
        from_attributes = True