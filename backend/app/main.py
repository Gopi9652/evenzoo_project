from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.models import *
from app.routers import auth, vendor, booking, payment, review, notification, admin,location, wishlist
from app.routers import websocket as ws_router
from app.routers import message
from app.routers import event_post



Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Evenzoo API",
    description="Event Vendor Marketplace",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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

@app.get("/")
def root():
    return {"message": "Evenzoo API running ✅"}