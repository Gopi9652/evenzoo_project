from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import re
from pydantic import field_validator

COMMON = {"password", "password1", "12345678", "123456789", "qwerty123", "iloveyou", "admin123", "welcome1", "evenzoo1"}

def validate_password_strength(v: str) -> str:
    if len(v) < 8:
        raise ValueError("Password must be at least 8 characters")
    if len(v.encode()) > 72:                    # bcrypt silently truncates beyond 72 bytes
        raise ValueError("Password must be at most 72 characters")
    if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
        raise ValueError("Password must contain letters and numbers")
    if v.lower() in COMMON:
        raise ValueError("That password is too common")
    return v

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    role: str  # customer or vendor
    _pw = field_validator("password")(validate_password_strength)

class RegisterResponse(BaseModel):
    message: str
    user_id: int

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    name: str
'''
class SendOTPRequest(BaseModel):
    phone: str
    purpose: str  # register / login / reset_password

class VerifyOTPRequest(BaseModel):
    phone: str
    otp_code: str
    purpose: str

'''
class SendOTPRequest(BaseModel):
    email: EmailStr
    purpose: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str
    purpose: str

class OTPResponse(BaseModel):
    message: str
    verified: bool

class RefreshRequest(BaseModel):
    refresh_token: str

class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    _pw = field_validator("new_password")(validate_password_strength)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    role: str
    is_verified: bool
    profile_photo: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str



class SessionResponse(BaseModel):
    id: int
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    last_used_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True