from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import *
from app.routers import auth, vendor, booking, payment, review, notification, admin,location, wishlist
from app.routers import websocket as ws_router
from app.routers import message
from app.routers import event_post
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.utils.rate_limiter import limiter
from app.routers import privacy, account

from app.config import settings
from app.routers import quote



docs_enabled = settings.ENVIRONMENT != "production"

app = FastAPI(
    title="Evenzoo API",
    description="Event Vendor Marketplace",
    version="1.0.0",
    docs_url="/docs" if docs_enabled else None,
    redoc_url="/redoc" if docs_enabled else None,
    openapi_url="/openapi.json" if docs_enabled else None,
)

# ── Rate Limiting Setup ──
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
#allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(",")]
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Configure CORS using environment settings
allowed_origins = [
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


import logging
from fastapi.responses import JSONResponse
logger = logging.getLogger("evenzoo")

@app.exception_handler(Exception)
async def unhandled_exception(request: Request, exc: Exception):
    logger.exception("Unhandled error %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Something went wrong. Please try again."})

app.include_router(ws_router.router)
app.include_router(auth.router,         prefix="/api/auth")
app.include_router(vendor.router,       prefix="/api/vendors")
app.include_router(booking.router,      prefix="/api/bookings")
app.include_router(payment.router,      prefix="/api/payments")
app.include_router(review.router,       prefix="/api/reviews")
app.include_router(notification.router, prefix="/api/notifications")
app.include_router(admin.router,        prefix="/api/admin")
app.include_router(location.router,        prefix="/api/location")
app.include_router(wishlist.router, prefix="/api/wishlist")
app.include_router(message.router, prefix="/api/messages")
app.include_router(event_post.router, prefix="/api/event-posts")
app.include_router(privacy.router, prefix="/api/privacy")
app.include_router(account.router, prefix="/api/account")
app.include_router(quote.router, prefix="/api/quotes")
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Evenzoo API running ✅"}
