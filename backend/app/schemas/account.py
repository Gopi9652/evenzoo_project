from pydantic import BaseModel, EmailStr
from typing import Optional


class ChangeEmailRequest(BaseModel):
    new_email: EmailStr
    current_password: str   # re-confirm identity before allowing a sensitive change


class ConfirmEmailChangeRequest(BaseModel):
    token: str


class ChangePhoneRequest(BaseModel):
    new_phone: str
    current_password: str


class VerifyPhoneChangeRequest(BaseModel):
    otp_code: str


class PendingChangesResponse(BaseModel):
    pending_email: Optional[str] = None
    pending_phone: Optional[str] = None