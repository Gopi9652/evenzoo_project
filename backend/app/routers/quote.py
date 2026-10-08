from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, get_customer, get_vendor
from app.models.user import User
from app.services.quote_service import quote_service
from app.schemas.quote import (
    QuoteRequestCreate, QuoteOfferCreate, QuoteResponse, QuoteStatusUpdate, BundleQuoteCreate
)
from datetime import datetime
router = APIRouter(tags=["Quotes"])

from decimal import Decimal
from pydantic import BaseModel

class DirectQuoteCreate(BaseModel):
    event_post_id: int
    quoted_amount: Decimal
    category_id: Optional[int] = None
    message: Optional[str] = None

@router.post("/offer-direct", response_model=QuoteResponse)
def offer_quote_direct(
    data: DirectQuoteCreate,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return quote_service.offer_quote_direct(
        db, current_user.id, data.event_post_id, data.category_id, data.quoted_amount, data.message
    )
@router.post("/request", response_model=QuoteResponse)
def request_quote(
    data: QuoteRequestCreate,
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return quote_service.request_quote(db, current_user.id, data)


@router.put("/{quote_id}/respond", response_model=QuoteResponse)
def respond_to_quote(
    quote_id: int,
    data: QuoteOfferCreate,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return quote_service.respond_to_quote(db, current_user.id, quote_id, data)


@router.put("/{quote_id}/status", response_model=QuoteResponse)
def update_quote_status(
    quote_id: int,
    data: QuoteStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return quote_service.update_quote_status(db, current_user.id, quote_id, data.status)




@router.get("/my", response_model=List[QuoteResponse])
def get_my_quotes(
    category_id: Optional[int] = Query(None),
    event_post_id: Optional[int] = Query(None),
    days: Optional[int] = Query(30),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return quote_service.get_my_quotes_as_customer(db, current_user.id, category_id, event_post_id, days, from_date, to_date)


@router.get("/vendor-received", response_model=List[QuoteResponse])
def get_vendor_quotes(
    category_id: Optional[int] = Query(None),
    days: Optional[int] = Query(30),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return quote_service.get_my_quotes_as_vendor(db, current_user.id, category_id, days, from_date, to_date)

@router.post("/offer-bundle", response_model=List[QuoteResponse])
def offer_bundle_quote(
    data: BundleQuoteCreate,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return quote_service.offer_bundle_quote(db, current_user.id, data.event_post_id, data.items, data.message)
from app.schemas.quote import QuotePostSummary

@router.get("/my", response_model=List[QuoteResponse])
def get_my_quotes(
    category_id: Optional[int] = Query(None),
    event_post_id: Optional[int] = Query(None),   # ← new
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return quote_service.get_my_quotes_as_customer(db, current_user.id, category_id, event_post_id)


@router.get("/my/summary-by-post", response_model=List[QuotePostSummary])
def get_quote_summary(
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return quote_service.get_quote_summary_by_post(db, current_user.id)