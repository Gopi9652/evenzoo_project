from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
import secrets

from app.models.user import User, OTPVerification
from app.utils.security import verify_password
from app.utils.otp import generate_otp, otp_expiry
from app.utils.sms import send_otp_sms
from app.schemas.account import ChangeEmailRequest, ChangePhoneRequest


class AccountService_:

    # ── EMAIL CHANGE (staged, confirmed via emailed link) ──

    def request_email_change(self, db: Session, user_id: int, data: ChangeEmailRequest):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )

        if data.new_email == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This is already your current email"
            )

        existing = db.query(User).filter(User.email == data.new_email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email is already in use by another account"
            )

        # Stage the change — does NOT take effect until confirmed
        user.pending_email = data.new_email
        db.commit()

        # Generate a confirmation token (reusing OTPVerification table generically
        # as a single-use token store, since it already has the shape we need)
        token = secrets.token_urlsafe(32)
        db.add(OTPVerification(
            user_id=user.id,
            otp_code=token,
            purpose="email_change",
            expires_at=otp_expiry(60)  # 1 hour to confirm
        ))
        db.commit()

        # TODO: send this link via real email once email sending is added (see earlier build notes)
        confirm_link = f"https://evenzoo.vercel.app/settings/confirm-email?token={token}"
        print(f"[DEV MODE] Email change confirmation link for {data.new_email}: {confirm_link}")

        return {"message": f"A confirmation link has been sent to {data.new_email}. Your email will not change until you confirm it."}


    def confirm_email_change(self, db: Session, token: str):
        record = db.query(OTPVerification).filter(
            OTPVerification.otp_code == token,
            OTPVerification.purpose == "email_change",
            OTPVerification.is_used == False,
            OTPVerification.expires_at > datetime.utcnow()
        ).first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired confirmation link"
            )

        user = db.query(User).filter(User.id == record.user_id).first()
        if not user or not user.pending_email:
            raise HTTPException(status_code=404, detail="No pending email change found")

        # Re-check uniqueness at confirmation time too, in case someone else
        # claimed the email in the window between request and confirmation
        existing = db.query(User).filter(
            User.email == user.pending_email,
            User.id != user.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email was claimed by another account before you confirmed. Please try a different email."
            )

        user.email = user.pending_email
        user.pending_email = None
        record.is_used = True

        db.commit()
        return {"message": "Email updated successfully. Please log in again with your new email."}


    def cancel_email_change(self, db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.pending_email = None
        db.commit()
        return {"message": "Pending email change cancelled"}


    # ── PHONE CHANGE (staged, confirmed via OTP — mirrors registration flow) ──

    def request_phone_change(self, db: Session, user_id: int, data: ChangePhoneRequest):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )

        if data.new_phone == user.phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This is already your current phone number"
            )

        existing = db.query(User).filter(User.phone == data.new_phone).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This phone number is already in use by another account"
            )

        user.pending_phone = data.new_phone
        db.commit()

        # Invalidate any old pending OTPs for this purpose first
        db.query(OTPVerification).filter(
            OTPVerification.user_id == user.id,
            OTPVerification.purpose == "phone_change",
            OTPVerification.is_used == False
        ).update({"is_used": True})

        code = generate_otp()
        db.add(OTPVerification(
            user_id=user.id,
            otp_code=code,
            purpose="phone_change",
            expires_at=otp_expiry(10)
        ))
        db.commit()

        send_otp_sms(data.new_phone, code)

        return {"message": f"An OTP has been sent to {data.new_phone}. Enter it to confirm the change."}


    def verify_phone_change(self, db: Session, user_id: int, otp_code: str):
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.pending_phone:
            raise HTTPException(status_code=404, detail="No pending phone change found")

        record = db.query(OTPVerification).filter(
            OTPVerification.user_id == user.id,
            OTPVerification.otp_code == otp_code,
            OTPVerification.purpose == "phone_change",
            OTPVerification.is_used == False,
            OTPVerification.expires_at > datetime.utcnow()
        ).first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )

        # Re-check uniqueness at confirmation time too
        existing = db.query(User).filter(
            User.phone == user.pending_phone,
            User.id != user.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This number was claimed by another account before you confirmed. Please try a different number."
            )

        user.phone = user.pending_phone
        user.pending_phone = None
        record.is_used = True

        db.commit()
        return {"message": "Phone number updated successfully."}


    def cancel_phone_change(self, db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.pending_phone = None
        db.commit()
        return {"message": "Pending phone change cancelled"}


    def resend_phone_change_otp(self, db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.pending_phone:
            raise HTTPException(status_code=404, detail="No pending phone change found")

        db.query(OTPVerification).filter(
            OTPVerification.user_id == user.id,
            OTPVerification.purpose == "phone_change",
            OTPVerification.is_used == False
        ).update({"is_used": True})
        db.commit()

        code = generate_otp()
        db.add(OTPVerification(
            user_id=user.id,
            otp_code=code,
            purpose="phone_change",
            expires_at=otp_expiry(10)
        ))
        db.commit()

        send_otp_sms(user.pending_phone, code)
        return {"message": f"A new OTP has been sent to {user.pending_phone}"}


    def get_pending_changes(self, db: Session, user_id: int):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "pending_email": user.pending_email,
            "pending_phone": user.pending_phone
        }


account_service = AccountService_()