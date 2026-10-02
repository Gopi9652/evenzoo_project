from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.utils.security import decode_token
from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param

bearer = HTTPBearer()

def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    """
    Same as get_current_user, but returns None instead of raising 401
    when no valid token is present — lets a route behave differently
    for logged-in vs anonymous visitors without blocking either.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    scheme, token = get_authorization_scheme_param(auth_header)
    if scheme.lower() != "bearer" or not token:
        return None

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(
        User.id == payload.get("sub")
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    return user


def require_role(*roles: str):
    def checker(
        current_user: User = Depends(get_current_user)
    ):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required: {roles}"
            )
        return current_user
    return checker


def get_customer(
    user: User = Depends(require_role("customer"))
):
    return user

def get_vendor(
    user: User = Depends(require_role("vendor"))
):
    return user

def get_admin(
    user: User = Depends(require_role("admin"))
):
    return user