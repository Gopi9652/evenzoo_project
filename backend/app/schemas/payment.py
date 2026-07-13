from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ── CREATE ORDER ──
class CreateOrderRequest(BaseModel):
    booking_id: int


class CreateOrderResponse(BaseModel):
    order_id:  str
    amount:    int       # in paise
    currency:  str
    key_id:    str        # frontend needs this to open checkout
    booking_ref: str


# ── VERIFY PAYMENT ──
class VerifyPaymentRequest(BaseModel):
    booking_id:          int
    razorpay_order_id:   str
    razorpay_payment_id: str
    razorpay_signature:  str


# ── PAYMENT RESPONSE ──
class PaymentResponse(BaseModel):
    id:                  int
    booking_id:          int
    razorpay_order_id:   Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    amount:              Decimal
    currency:            str
    status:              str
    payment_method:      Optional[str] = None
    paid_at:             Optional[datetime] = None
    created_at:          datetime

    class Config:
        from_attributes = True


# ── REFUND ──
class RefundRequest(BaseModel):
    booking_id: int
    amount:     Optional[Decimal] = None  # None = full refund
    reason:     str


class RefundResponse(BaseModel):
    id:                 int
    payment_id:         int
    razorpay_refund_id: Optional[str] = None
    amount:             Decimal
    reason:             Optional[str] = None
    status:             str
    created_at:         datetime

    class Config:
        from_attributes = True