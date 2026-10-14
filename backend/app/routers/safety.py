from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Request
from starlette.concurrency import run_in_threadpool
from app.utils.rate_limiter import limiter, get_real_client_ip
from pydantic import BaseModel
from typing import Optional, List, Field
from datetime import datetime
from decimal import Decimal

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, get_vendor, get_optional_current_user
from app.models.user import User
from app.services.vendor_service import vendor_service
from app.models.safety import UserBlock, UserReport
router = APIRouter(tags=["Safety"])

@router.post("/block/{user_id}")
def block(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id == current_user.id:
        raise HTTPException(400, "You can't block yourself")
    if not db.query(UserBlock).filter_by(blocker_id=current_user.id, blocked_id=user_id).first():
        db.add(UserBlock(blocker_id=current_user.id, blocked_id=user_id)); db.commit()
    return {"message": "User blocked"}

@router.delete("/block/{user_id}")
def unblock(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(UserBlock).filter_by(blocker_id=current_user.id, blocked_id=user_id).delete(); db.commit()
    return {"message": "User unblocked"}

class ReportCreate(BaseModel):
    user_id: int
    reason: str = Field(max_length=50)
    details: Optional[str] = Field(None, max_length=1000)

@router.post("/report")
@limiter.limit("10/day")
def report(request: Request, data: ReportCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.add(UserReport(reporter_id=current_user.id, reported_user_id=data.user_id, reason=data.reason, details=data.details))
    db.commit()
    return {"message": "Report submitted. Our team will review it."}