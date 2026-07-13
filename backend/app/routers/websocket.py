from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.utils.websocket_manager import manager
from app.utils.security import decode_token

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        await websocket.close(code=1008)
        return

    user_id = payload.get("sub")
    await manager.connect(user_id, websocket)

    try:
        while True:
            # Keep connection alive, listen for any client pings
            data = await websocket.receive_text()
            # Currently we don't need to process incoming messages here (chat feature will extend this)
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)