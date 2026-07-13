from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    role: str  # customer or vendor

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

class SendOTPRequest(BaseModel):
    phone: str
    purpose: str  # register / login / reset_password

class VerifyOTPRequest(BaseModel):
    phone: str
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

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    role: str
    is_verified: bool
    profile_photo: Optional[str] = None

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