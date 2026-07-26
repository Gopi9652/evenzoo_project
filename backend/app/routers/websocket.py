from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Query
)

from app.utils.websocket_manager import manager
from app.utils.security import decode_token


router = APIRouter(
    tags=["WebSocket"]
)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):

    user_id = None

    try:

        print("🔌 WebSocket connection request received")

        # Decode token
        payload = decode_token(token)

        print("JWT Payload:", payload)

        # Validate token
        if (
            not payload
            or payload.get("type") != "access"
        ):

            print("❌ Invalid WebSocket token")

            await websocket.close(
                code=1008
            )

            return

        # Get user ID from JWT
        user_id = payload.get("sub")

        if not user_id:

            print("❌ User ID missing")

            await websocket.close(
                code=1008
            )

            return

        # Convert string "5" → integer 5
        user_id = int(user_id)

        print(
            f"👤 WebSocket user ID: {user_id}"
        )

        # Store connection
        await manager.connect(
            user_id,
            websocket
        )

        # Temporary test message
        await websocket.send_json({

            "type": "connection",

            "message":
                "WebSocket connected successfully",

            "user_id":
                user_id

        })

        # Keep connection alive
        while True:

            data = await websocket.receive_text()

            print(
                f"📩 Received from user {user_id}:",
                data
            )

    except WebSocketDisconnect:

        print(
            f"🔴 User {user_id} disconnected"
        )

        if user_id is not None:

            manager.disconnect(
                user_id,
                websocket
            )

    except Exception as error:

        print(
            f"❌ WebSocket error for user {user_id}:",
            error
        )

        if user_id is not None:

            manager.disconnect(
                user_id,
                websocket
            )