
import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import decode_token
from app.utils.websocket_manager import manager

router = APIRouter(tags=["WebSocket"])

logger = logging.getLogger(__name__)

AUTH_TIMEOUT = 5
MAX_FRAME_BYTES = 4096

ALLOWED_ORIGINS = {
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip()
}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    user_id = None
    connected = False

    # 1. Validate the connection origin.
    origin = websocket.headers.get("origin")

    if origin and origin not in ALLOWED_ORIGINS:
        logger.warning("Rejected WebSocket origin: %s", origin)
        await websocket.close(code=1008)
        return

    # Accept the connection before receiving the authentication message.
    await websocket.accept()

    try:
        logger.info("WebSocket connection request received")

        # 2. Authenticate within five seconds.
        try:
            raw_message = await asyncio.wait_for(
                websocket.receive_text(),
                timeout=AUTH_TIMEOUT
            )

            if len(raw_message.encode("utf-8")) > MAX_FRAME_BYTES:
                logger.warning("WebSocket authentication frame too large")
                await websocket.close(code=1008)
                return

            message = json.loads(raw_message)

        except asyncio.TimeoutError:
            logger.warning("WebSocket authentication timed out")
            await websocket.close(code=1008)
            return

        except json.JSONDecodeError:
            logger.warning("Invalid WebSocket authentication JSON")
            await websocket.close(code=1008)
            return

        # 3. Require the expected authentication message.
        if not isinstance(message, dict) or message.get("type") != "auth":
            logger.warning("Missing or invalid WebSocket auth message")
            await websocket.close(code=1008)
            return

        token = message.get("token")

        if not isinstance(token, str) or not token:
            logger.warning("WebSocket token is missing")
            await websocket.close(code=1008)
            return

        # 4. Decode and validate the access token.
        try:
            payload = decode_token(token)
        except Exception:
            logger.warning("WebSocket token decoding failed")
            await websocket.close(code=1008)
            return

        if not payload or payload.get("type") != "access":
            logger.warning("Invalid WebSocket access token")
            await websocket.close(code=1008)
            return

        subject = payload.get("sub")

        if subject is None:
            logger.warning("User ID missing from WebSocket token")
            await websocket.close(code=1008)
            return

        try:
            user_id = int(subject)
        except (TypeError, ValueError):
            logger.warning("Invalid WebSocket user ID")
            await websocket.close(code=1008)
            return

        if user_id <= 0:
            logger.warning("WebSocket user ID must be positive")
            await websocket.close(code=1008)
            return

        logger.info("WebSocket authentication for user %s", user_id)

        # 5. Verify that the user exists and is active.
        db = SessionLocal()

        try:
            user = (
                db.query(User)
                .filter(User.id == user_id)
                .first()
            )

            if not user or not user.is_active:
                logger.warning(
                    "WebSocket rejected for inactive or missing user %s",
                    user_id
                )
                await websocket.close(code=1008)
                return

        finally:
            db.close()

        # 6. Register the authenticated connection.
        await manager.connect(user_id, websocket)
        connected = True

        logger.info("WebSocket connected for user %s", user_id)

        # Confirm successful authentication to the Angular client.
        await websocket.send_json({
            "type": "connection",
            "message": "WebSocket connected successfully",
            "user_id": user_id
        })

        # 7. Receive messages and enforce the frame-size/rate limits.
        while True:
            data = await websocket.receive_text()

            if len(data.encode("utf-8")) > MAX_FRAME_BYTES:
                logger.warning(
                    "Oversized WebSocket message from user %s",
                    user_id
                )
                await websocket.close(code=1008)
                break

            # Keep your existing rate-limit function here.
            if _is_rate_limited(user_id):
                logger.warning(
                    "WebSocket rate limit exceeded for user %s",
                    user_id
                )
                await websocket.close(code=1008)
                break

            logger.info(
                "WebSocket message received from user %s",
                user_id
            )

            # Add your existing message-handling logic here.
            # Do not trust client messages to authorize actions.

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for user %s", user_id)

    except Exception:
        logger.exception("WebSocket error for user %s", user_id)

        if not connected:
            try:
                await websocket.close(code=1011)
            except Exception:
                pass

    finally:
        if connected and user_id is not None:
            manager.disconnect(user_id, websocket)
            logger.info("WebSocket cleanup completed for user %s", user_id)