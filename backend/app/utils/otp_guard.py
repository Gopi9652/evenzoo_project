import hmac
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy import func
from app.models.user import OTPVerification
from app.config import settings

MAX_ATTEMPTS = 5
MAX_PER_PHONE_PER_HOUR = 3
MAX_SMS_PER_DAY = 500


def check_otp(db, candidates_query, submitted: str) -> bool:
    """candidates_query = unused, unexpired OTP rows for this purpose/identity."""
    record = candidates_query.order_by(OTPVerification.created_at.desc()).first()
    if not record:
        return False
    if record.attempts >= MAX_ATTEMPTS:
        record.is_used = True
        db.commit()
        raise HTTPException(429, "Too many incorrect attempts. Request a new code.")
    if hmac.compare_digest(str(record.otp_code), str(submitted)):
        record.is_used = True
        db.commit()
        return True
    record.attempts += 1
    if record.attempts >= MAX_ATTEMPTS:
        record.is_used = True
    db.commit()
    return False


def assert_sms_budget(db, identity_filter):
    """Call before generating any OTP. identity_filter = SQLAlchemy condition for this phone/user."""
    now = datetime.utcnow()
    recent = db.query(func.count(OTPVerification.id)).filter(
        identity_filter, OTPVerification.created_at > now - timedelta(hours=1)).scalar()
    if recent >= MAX_PER_PHONE_PER_HOUR:
        raise HTTPException(429, "Too many codes requested. Try again later.")
    today = db.query(func.count(OTPVerification.id)).filter(
        OTPVerification.created_at > now - timedelta(days=1)).scalar()
    if today >= MAX_SMS_PER_DAY:      # global circuit breaker on your MSG91 bill
        raise HTTPException(503, "Verification is temporarily unavailable.")