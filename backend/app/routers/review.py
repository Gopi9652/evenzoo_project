from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, get_customer, get_vendor
from app.models.user import User
from app.services.review_service import review_service
from app.schemas.review import ReviewCreate, ReviewReplyCreate, ReviewResponse
from app.schemas.review import ReviewUpdate

router = APIRouter(tags=["Reviews"])


@router.post("", response_model=ReviewResponse)
def create_review(
    data: ReviewCreate,
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return review_service.create_review(db, current_user.id, data)


@router.get("/vendor/{vendor_id}", response_model=List[ReviewResponse])
def get_vendor_reviews(
    vendor_id: int,
    db: Session = Depends(get_db)
):
    return review_service.get_vendor_reviews(db, vendor_id)


@router.put("/{review_id}/reply", response_model=ReviewResponse)
def reply_to_review(
    review_id: int,
    data: ReviewReplyCreate,
    current_user: User = Depends(get_vendor),
    db: Session = Depends(get_db)
):
    return review_service.reply_to_review(
        db, current_user.id, review_id, data
    )



@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    data: ReviewUpdate,
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return review_service.update_review(db, current_user.id, review_id, data)


@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return review_service.delete_review(db, current_user.id, review_id)

@router.get("/my", response_model=List[ReviewResponse])
def get_my_reviews(
    current_user: User = Depends(get_customer),
    db: Session = Depends(get_db)
):
    return review_service.get_my_reviews(db, current_user.id)