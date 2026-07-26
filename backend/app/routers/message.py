from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.services.message_service import message_service
from app.schemas.message import MessageCreate, MessageResponse, ConversationSummary

router = APIRouter(tags=["Messages"])


@router.post("", response_model=MessageResponse)
async def send_message(
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return await message_service.send_message(db, current_user.id, data)


@router.get("/conversations", response_model=List[ConversationSummary])
def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return message_service.get_my_conversations(db, current_user.id)


@router.get("/booking/{booking_id}", response_model=List[MessageResponse])
def get_conversation_by_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return message_service.get_conversation_by_booking(db, current_user.id, booking_id)


@router.get("/user/{other_user_id}", response_model=List[MessageResponse])
def get_conversation_direct(
    other_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return message_service.get_conversation_direct(db, current_user.id, other_user_id)