from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
import razorpay.errors

from app.models.payment import Payment, Refund, VendorPayout
from app.models.booking import Booking
from app.models.vendor import VendorProfile
from app.schemas.payment import CreateOrderRequest, VerifyPaymentRequest, RefundRequest
from app.utils.razorpay_client import client
from app.config import settings


class PaymentService_:

    # ── CREATE RAZORPAY ORDER ──
    def create_order(
        self, db: Session,
        customer_id: int,
        data: CreateOrderRequest
    ):
        booking = db.query(Booking).filter(
            Booking.id          == data.booking_id,
            Booking.customer_id == customer_id
        ).first()

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )

        if booking.status != "confirmed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking must be confirmed by vendor before payment"
            )

        # Check if payment already exists and captured
        existing_payment = db.query(Payment).filter(
            Payment.booking_id == booking.id,
            Payment.status == "captured"
        ).first()

        if existing_payment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already completed for this booking"
            )

        # Amount in paise (Razorpay requires smallest currency unit)
        amount_paise = int(float(booking.total_amount) * 100)

        # Create order on Razorpay
        try:
            razorpay_order = client.order.create({
                "amount": amount_paise,
                "currency": "INR",
                "receipt": booking.booking_ref,
                "notes": {
                    "booking_id": str(booking.id),
                    "booking_ref": booking.booking_ref
                }
            })
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Razorpay order creation failed: {str(e)}"
            )

        # Save payment record as pending
        payment = Payment(
            booking_id=booking.id,
            razorpay_order_id=razorpay_order["id"],
            amount=booking.total_amount,
            currency="INR",
            status="pending"
        )
        db.add(payment)
        db.commit()

        return {
            "order_id":    razorpay_order["id"],
            "amount":      amount_paise,
            "currency":    "INR",
            "key_id":      settings.RAZORPAY_KEY_ID,
            "booking_ref": booking.booking_ref
        }


    # ── VERIFY PAYMENT SIGNATURE ──
    def verify_payment(
        self, db: Session,
        customer_id: int,
        data: VerifyPaymentRequest
    ):
        booking = db.query(Booking).filter(
            Booking.id          == data.booking_id,
            Booking.customer_id == customer_id
        ).first()

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )

        payment = db.query(Payment).filter(
            Payment.booking_id        == booking.id,
            Payment.razorpay_order_id == data.razorpay_order_id
        ).first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment record not found"
            )

        # Verify signature using Razorpay SDK
        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id":   data.razorpay_order_id,
                "razorpay_payment_id": data.razorpay_payment_id,
                "razorpay_signature":  data.razorpay_signature
            })
        except razorpay.errors.SignatureVerificationError:
            payment.status = "failed"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment signature verification failed"
            )

        # Signature valid — mark payment captured
        payment.razorpay_payment_id = data.razorpay_payment_id
        payment.razorpay_signature  = data.razorpay_signature
        payment.status              = "captured"
        payment.paid_at             = datetime.utcnow()

        # Create vendor payout record (pending until manual/auto transfer)
        vendor = db.query(VendorProfile).filter(
            VendorProfile.id == booking.vendor_id
        ).first()

        payout = VendorPayout(
            vendor_id=vendor.id,
            booking_id=booking.id,
            amount=booking.vendor_amount,
            status="pending"
        )
        db.add(payout)

        db.commit()
        db.refresh(payment)

        return {
            "message": "Payment verified successfully",
            "payment_id": payment.id,
            "status": payment.status
        }


    # ── RAZORPAY WEBHOOK HANDLER ──
    def handle_webhook(
        self, db: Session,
        payload: dict,
        signature: str,
        webhook_secret: str
    ):
        # Verify webhook signature
        try:
            client.utility.verify_webhook_signature(
                str(payload), signature, webhook_secret
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook signature"
            )

        event = payload.get("event")

        if event == "payment.captured":
            razorpay_order_id = payload["payload"]["payment"]["entity"]["order_id"]
            payment = db.query(Payment).filter(
                Payment.razorpay_order_id == razorpay_order_id
            ).first()

            if payment and payment.status != "captured":
                payment.status = "captured"
                payment.paid_at = datetime.utcnow()
                db.commit()

        elif event == "payment.failed":
            razorpay_order_id = payload["payload"]["payment"]["entity"]["order_id"]
            payment = db.query(Payment).filter(
                Payment.razorpay_order_id == razorpay_order_id
            ).first()

            if payment:
                payment.status = "failed"
                db.commit()

        return {"message": "Webhook processed"}


    # ── GET PAYMENT STATUS ──
    def get_payment(
        self, db: Session,
        booking_id: int,
        user_id: int
    ):
        booking = db.query(Booking).filter(
            Booking.id == booking_id
        ).first()

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )

        vendor = db.query(VendorProfile).filter(
            VendorProfile.user_id == user_id
        ).first()

        is_customer = booking.customer_id == user_id
        is_vendor   = vendor and booking.vendor_id == vendor.id

        if not is_customer and not is_vendor:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        payment = db.query(Payment).filter(
            Payment.booking_id == booking_id
        ).first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="No payment found for this booking"
            )

        return payment


    # ── INITIATE REFUND ──
    def initiate_refund(
        self, db: Session,
        user_id: int,
        data: RefundRequest
    ):
        booking = db.query(Booking).filter(
            Booking.id == data.booking_id
        ).first()

        if not booking:
            raise HTTPException(
                status_code=404,
                detail="Booking not found"
            )

        payment = db.query(Payment).filter(
            Payment.booking_id == booking.id,
            Payment.status     == "captured"
        ).first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No captured payment found for this booking"
            )

        refund_amount = data.amount if data.amount else payment.amount
        amount_paise  = int(float(refund_amount) * 100)

        # Create refund on Razorpay
        try:
            razorpay_refund = client.payment.refund(
                payment.razorpay_payment_id,
                {"amount": amount_paise}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Razorpay refund failed: {str(e)}"
            )

        refund = Refund(
            payment_id=payment.id,
            razorpay_refund_id=razorpay_refund["id"],
            amount=refund_amount,
            reason=data.reason,
            status="processed",
            initiated_by=user_id,
            processed_at=datetime.utcnow()
        )
        db.add(refund)

        payment.status = "refunded"

        db.commit()
        db.refresh(refund)
        return refund


payment_service = PaymentService_()