from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request
from app.config import settings

def get_real_client_ip(request: Request) -> str:
    """
    Railway and most reverse proxies pass the real client IP via the
    X-Forwarded-For header. Fall back to the direct connection IP
    if that header isn't present (e.g. local development).
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)



def get_real_client_ip(request: Request) -> str:
    # Each trusted proxy appends the address it saw, so the Nth entry from the
    # RIGHT is the real client. Anything to the left is client-supplied.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        parts = [p.strip() for p in forwarded.split(",") if p.strip()]
        n = settings.TRUSTED_PROXY_COUNT
        if parts and 0 < n <= len(parts):
            return parts[-n]
    return request.client.host if request.client else "unknown"


limiter = Limiter(
    key_func=get_real_client_ip,
    storage_uri=settings.REDIS_URL or "memory://",   # see C18
)