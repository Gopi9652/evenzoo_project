from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, get_admin
from app.models.user import User
from app.services.privacy_service import privacy_service
from app.schemas.privacy import (
    DeletionRequestCreate, DeletionRequestResponse, UserDataExport
)

router = APIRouter(tags=["Privacy"])


# ── USER-FACING ──

@router.post("/deletion-request", response_model=DeletionRequestResponse)
def request_account_deletion(
    data: DeletionRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return privacy_service.request_deletion(db, current_user.id, data)


@router.get("/deletion-request/my", response_model=List[DeletionRequestResponse])
def get_my_deletion_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return privacy_service.get_my_deletion_requests(db, current_user.id)


@router.delete("/deletion-request/{request_id}")
def cancel_deletion_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return privacy_service.cancel_deletion_request(db, current_user.id, request_id)


@router.get("/export-my-data", response_model=UserDataExport)
def export_my_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return privacy_service.export_my_data(db, current_user.id)


# ── ADMIN ──

@router.get("/admin/deletion-requests")
def get_pending_deletion_requests(
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return privacy_service.get_pending_deletion_requests(db)


@router.put("/admin/deletion-requests/{request_id}/process")
def process_deletion_request(
    request_id: int,
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return privacy_service.process_deletion(db, current_user.id, request_id)


@router.put("/admin/deletion-requests/{request_id}/reject")
def reject_deletion_request(
    request_id: int,
    reason: str,
    current_user: User = Depends(get_admin),
    db: Session = Depends(get_db)
):
    return privacy_service.reject_deletion(db, current_user.id, request_id, reason)