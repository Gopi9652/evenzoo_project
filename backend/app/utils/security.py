from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    payload = data.copy()
    if "sub" in payload:
        payload["sub"] = str(payload["sub"])
    payload["exp"] = datetime.utcnow() + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )
    payload["type"] = "access"
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    if "sub" in payload:
        payload["sub"] = str(payload["sub"])
    payload["exp"] = datetime.utcnow() + timedelta(
        days=settings.JWT_REFRESH_EXPIRE_DAYS
    )
    payload["type"] = "refresh"
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
    except JWTError:
        return None