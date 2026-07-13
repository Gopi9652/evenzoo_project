from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    RegisterRequest, RegisterResponse,
    LoginRequest, LoginResponse,
    SendOTPRequest, VerifyOTPRequest, OTPResponse,
    RefreshRequest, RefreshResponse,
    ForgotPasswordRequest, ResetPasswordRequest,
    UserResponse,ChangePasswordRequest
)
from app.services.auth_service import auth_service
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from fastapi import UploadFile, File
from app.utils.cloudinary_client import upload_image
from typing import List
from app.schemas.auth import SessionResponse    

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=RegisterResponse)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    return auth_service.register(db, data)


from fastapi import Request

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    return auth_service.login(db, data, user_agent, ip_address)


@router.post("/send-otp")
def send_otp(
    data: SendOTPRequest,
    db: Session = Depends(get_db)
):
    return auth_service.send_otp(db, data.phone, data.purpose)


@router.post("/verify-otp", response_model=OTPResponse)
def verify_otp(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):
    return auth_service.verify_otp(
        db, data.phone, data.otp_code, data.purpose
    )


@router.post("/refresh", response_model=RefreshResponse)
def refresh(
    data: RefreshRequest,
    db: Session = Depends(get_db)
):
    return auth_service.refresh_token(db, data.refresh_token)


@router.post("/logout")
def logout(
    data: RefreshRequest,
    db: Session = Depends(get_db)
):
    return auth_service.logout(db, data.refresh_token)


@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    return auth_service.forgot_password(db, data.email)


@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    return auth_service.reset_password(
        db, data.token, data.new_password
    )


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.put("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return auth_service.change_password(
        db, current_user.id, data.current_password, data.new_password
    )



@router.post("/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    photo_url = upload_image(file.file, folder="evenzoo/avatars")
    current_user.profile_photo = photo_url
    db.commit()
    db.refresh(current_user)
    return {"profile_photo": photo_url}



@router.get("/sessions", response_model=List[SessionResponse])
def get_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return auth_service.get_sessions(db, current_user.id)


@router.delete("/sessions/{session_id}")
def revoke_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return auth_service.revoke_session(db, current_user.id, session_id)


@router.delete("/sessions")
def revoke_all_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return auth_service.revoke_all_sessions(db, current_user.id)