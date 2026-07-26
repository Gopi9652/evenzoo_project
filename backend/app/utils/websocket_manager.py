from fastapi import WebSocket
from typing import Dict, List


class ConnectionManager:

    def __init__(self):
        # user_id -> multiple active WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(
        self,
        user_id: int,
        websocket: WebSocket
    ):
        # Accept WebSocket connection
        await websocket.accept()

        # Create list for new user
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        # Add this connection
        self.active_connections[user_id].append(websocket)

        print(
            f"✅ User {user_id} connected"
        )

        print(
            "Active connections:",
            self.active_connections
        )

    def disconnect(
        self,
        user_id: int,
        websocket: WebSocket
    ):

        if user_id not in self.active_connections:
            return

        if websocket in self.active_connections[user_id]:

            self.active_connections[user_id].remove(
                websocket
            )

        # If no connections remain
        if not self.active_connections[user_id]:

            del self.active_connections[user_id]

        print(
            f"🔴 User {user_id} disconnected"
        )

    async def send_to_user(
        self,
        user_id: int,
        message: dict
    ):

        print(
            f"📤 Sending message to user {user_id}"
        )

        print(
            "Active users:",
            list(self.active_connections.keys())
        )

        # User is offline
        if user_id not in self.active_connections:

            print(
                f"⚠️ User {user_id} is offline"
            )

            return

        dead_connections = []

        # Send to every device/tab of the user
        for websocket in self.active_connections[user_id]:

            try:

                await websocket.send_json(message)

                print(
                    f"✅ Message sent to user {user_id}"
                )

            except Exception as error:

                print(
                    f"❌ Failed to send message: {error}"
                )

                dead_connections.append(websocket)

        # Remove dead connections
        for websocket in dead_connections:

            self.disconnect(
                user_id,
                websocket
            )

    def is_online(
        self,
        user_id: int
    ) -> bool:

        return (
            user_id in self.active_connections
            and len(
                self.active_connections[user_id]
            ) > 0
        )


# Create one global manager instance
manager = ConnectionManager()