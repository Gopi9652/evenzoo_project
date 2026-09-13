from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
import secrets

from app.models.user import User, OTPVerification, RefreshToken, PasswordReset
from app.models.vendor import VendorProfile
from app.models.customer import CustomerProfile
from app.schemas.auth import RegisterRequest, LoginRequest
from app.utils.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token
)
from app.utils.otp import generate_otp, otp_expiry

from app.utils.sms import send_otp_sms
class AuthService:

    def register(self, db: Session, data: RegisterRequest):
        # Check email
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        # Check phone
        if db.query(User).filter(User.phone == data.phone).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        # Validate role
        if data.role not in ["customer", "vendor"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role must be customer or vendor"
            )

        # Create user
        user = User(
            name=data.name,
            email=data.email,
            phone=data.phone,
            password_hash=hash_password(data.password),
            role=data.role,
            is_verified=False
        )
        db.add(user)
        db.flush()

        # Create profile
        if data.role == "vendor":
            db.add(VendorProfile(
                user_id=user.id,
                business_name=data.name
            ))
        else:
            db.add(CustomerProfile(user_id=user.id))

        db.commit()
        db.refresh(user)

        return {
            "message": "Registered successfully. Please verify OTP.",
            "user_id": user.id
        }


    def login(self, db: Session, data: LoginRequest, user_agent: str = None, ip_address: str = None):
        user = db.query(User).filter(
            User.email == data.email
        ).first()

        if not user or not verify_password(
            data.password, user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )

        access_token  = create_access_token(
            {"sub": user.id, "role": user.role}
        )
        refresh_token = create_refresh_token({"sub": user.id})

        # Simple device label from user agent
        device_label = self._parse_device(user_agent)

        db.add(RefreshToken(
            user_id=user.id,
            token=refresh_token,
            device_info=device_label,
            ip_address=ip_address,
            last_used_at=datetime.utcnow(),
            expires_at = datetime.utcnow() + timedelta(days=7)
        ))
        db.commit()

        return {
            "access_token":  access_token,
            "refresh_token": refresh_token,
            "token_type":    "bearer",
            "role":          user.role,
            "user_id":       user.id,
            "name":          user.name
        }

    def _parse_device(self, user_agent: str) -> str:
        if not user_agent:
            return "Unknown Device"
        ua = user_agent.lower()
        if "android" in ua:
            return "Android Device"
        elif "iphone" in ua or "ipad" in ua:
            return "iOS Device"
        elif "windows" in ua:
            return "Windows PC"
        elif "mac" in ua:
            return "Mac"
        else:
            return "Unknown Device"


    def send_otp(self, db: Session, phone: str, purpose: str):
        user = db.query(User).filter(User.phone == phone).first()
        '''
        if purpose == "register" and user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone already registered"
            )

        if purpose != "register" and not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number not found"
            )
        '''
        # Invalidate old OTPs
        if user:
            db.query(OTPVerification).filter(
                OTPVerification.user_id == user.id,
                OTPVerification.purpose == purpose,
                OTPVerification.is_used == False
            ).update({"is_used": True})

        code = generate_otp()
        db.add(OTPVerification(
            user_id=user.id if user else 0,
            otp_code=code,
            purpose=purpose,
            expires_at=otp_expiry(10)
        ))
        db.commit()

        # TODO: Send via SMS (MSG91 / Twilio)
        # For now print to console for testing
        print(f"OTP for {phone}: {code}")
        send_otp_sms(phone, code)

        return {"message": f"OTP sent to {phone}"}


    def verify_otp(
        self, db: Session,
        phone: str, otp_code: str, purpose: str
    ):
        user = db.query(User).filter(User.phone == phone).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        otp = db.query(OTPVerification).filter(
            OTPVerification.user_id   == user.id,
            OTPVerification.otp_code  == otp_code,
            OTPVerification.purpose   == purpose,
            OTPVerification.is_used   == False,
            OTPVerification.expires_at > datetime.utcnow()
        ).first()

        if not otp:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )

        otp.is_used = True

        if purpose == "register":
            user.is_verified = True

        db.commit()

        return {"message": "OTP verified successfully", "verified": True}


    def refresh_token(self, db: Session, token: str):
        payload = decode_token(token)

        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        rt = db.query(RefreshToken).filter(
            RefreshToken.token == token
        ).first()

        if not rt:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found"
            )

        user = db.query(User).filter(
            User.id == payload.get("sub")
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        new_access = create_access_token(
            {"sub": user.id, "role": user.role}
        )

        return {"access_token": new_access, "token_type": "bearer"}


    def logout(self, db: Session, token: str):
        db.query(RefreshToken).filter(
            RefreshToken.token == token
        ).delete()
        db.commit()
        return {"message": "Logged out successfully"}


    def forgot_password(self, db: Session, email: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=404,
                detail="Email not found"
            )

        token = secrets.token_urlsafe(32)
        db.add(PasswordReset(
            user_id=user.id,
            token=token,
            expires_at=otp_expiry(30)
        ))
        db.commit()

        # TODO: Send reset email
        print(f"Reset token: {token}")

        return {"message": "Password reset link sent to email"}


    def reset_password(
        self, db: Session,
        token: str, new_password: str
    ):
        reset = db.query(PasswordReset).filter(
            PasswordReset.token      == token,
            PasswordReset.is_used    == False,
            PasswordReset.expires_at > datetime.utcnow()
        ).first()

        if not reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )

        user = db.query(User).filter(
            User.id == reset.user_id
        ).first()

        user.password_hash = hash_password(new_password)
        reset.is_used = True
        db.commit()

        return {"message": "Password reset successfully"}
    
    def change_password(
            self, db: Session,
            user_id: int,
            current_password: str,
            new_password: str
        ):
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            if not verify_password(current_password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )

            if len(new_password) < 6:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New password must be at least 6 characters"
                )

            if verify_password(new_password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New password must be different from current password"
                )

            user.password_hash = hash_password(new_password)
            db.commit()

            # Invalidate all existing refresh tokens - forces re-login on other devices
            db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
            db.commit()

            return {"message": "Password changed successfully. Please log in again."}

    def get_sessions(self, db: Session, user_id: int):
            return db.query(RefreshToken).filter(
                RefreshToken.user_id == user_id
            ).order_by(RefreshToken.last_used_at.desc()).all()

    def revoke_session(self, db: Session, user_id: int, session_id: int):
        session = db.query(RefreshToken).filter(
            RefreshToken.id == session_id,
            RefreshToken.user_id == user_id
        ).first()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        db.delete(session)
        db.commit()
        return {"message": "Session revoked"}

    def revoke_all_sessions(self, db: Session, user_id: int, except_token: str = None):
        query = db.query(RefreshToken).filter(RefreshToken.user_id == user_id)
        if except_token:
            query = query.filter(RefreshToken.token != except_token)
        query.delete()
        db.commit()
        return {"message": "All other sessions revoked"}


auth_service = AuthService()