from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.services.notification_service import notification_service
from app.schemas.notification import NotificationResponse, UnreadCountResponse

router = APIRouter(tags=["Notifications"])


@router.get("", response_model=List[NotificationResponse])
def get_notifications(
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return notification_service.get_my_notifications(
        db, current_user.id, unread_only
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return notification_service.get_unread_count(db, current_user.id)


@router.put("/{notification_id}/read")
def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return notification_service.mark_read(
        db, current_user.id, notification_id
    )


@router.put("/read-all")
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return notification_service.mark_all_read(db, current_user.id)