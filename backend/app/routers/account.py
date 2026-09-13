from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.utils.rate_limiter import limiter
from fastapi import Request
from app.services.account_service import account_service
from app.schemas.account import (
    ChangeEmailRequest, ConfirmEmailChangeRequest,
    ChangePhoneRequest, VerifyPhoneChangeRequest,
    PendingChangesResponse
)

router = APIRouter(tags=["Account"])


@router.post("/change-email")
@limiter.limit("5/hour")
def request_email_change(
    request: Request,
    data: ChangeEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return account_service.request_email_change(db, current_user.id, data)


@router.post("/confirm-email-change")
def confirm_email_change(data: ConfirmEmailChangeRequest, db: Session = Depends(get_db)):
    return account_service.confirm_email_change(db, data.token)


@router.delete("/change-email")
def cancel_email_change(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return account_service.cancel_email_change(db, current_user.id)


@router.post("/change-phone")
@limiter.limit("5/hour")
def request_phone_change(
    request: Request,
    data: ChangePhoneRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return account_service.request_phone_change(db, current_user.id, data)


@router.post("/verify-phone-change")
@limiter.limit("10/hour")
def verify_phone_change(
    request: Request,
    data: VerifyPhoneChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return account_service.verify_phone_change(db, current_user.id, data.otp_code)


@router.post("/resend-phone-change-otp")
@limiter.limit("5/hour")
def resend_phone_change_otp(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return account_service.resend_phone_change_otp(db, current_user.id)


@router.delete("/change-phone")
def cancel_phone_change(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return account_service.cancel_phone_change(db, current_user.id)


@router.get("/pending-changes", response_model=PendingChangesResponse)
def get_pending_changes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return account_service.get_pending_changes(db, current_user.id)