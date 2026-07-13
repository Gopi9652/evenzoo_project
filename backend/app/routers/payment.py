from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.orm import Session
from typing import Optional
import json

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, get_customer
from app.models.user import User
from app.services.payment_service import payment_service
from app.schemas.payment import (
    CreateOrderRequest, CreateOrderResponse,
    VerifyPaymentRequest, PaymentResponse,
    RefundRequest, RefundResponse
)
from app.config import settings

router = APIRouter(tags=["Payments"])


@router.post("/create-order", response_model=CreateOrderResponse)
def create_order(
    data: CreateOrderRequest,
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return payment_service.create_order(db, current_user.id, data)


@router.post("/verify")
def verify_payment(
    data: VerifyPaymentRequest,
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return payment_service.verify_payment(db, current_user.id, data)


@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    body = await request.body()
    payload = json.loads(body)

    return payment_service.handle_webhook(
        db, payload, x_razorpay_signature,
        webhook_secret="your_webhook_secret_here"
    )


@router.get("/{booking_id}", response_model=PaymentResponse)
def get_payment_status(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return payment_service.get_payment(db, booking_id, current_user.id)


@router.post("/refund", response_model=RefundResponse)
def initiate_refund(
    data: RefundRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return payment_service.initiate_refund(db, current_user.id, data)