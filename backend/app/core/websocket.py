"""WebSocket connection manager for real-time meeting updates."""

import json

from fastapi import WebSocket


class WebSocketManager:
    """Manage WebSocket connections for meetings."""

    def __init__(self) -> None:
        # Map meeting_id -> list of active connections
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, meeting_id: str) -> None:
        """Accept WebSocket connection and subscribe to meeting."""
        await websocket.accept()
        if meeting_id not in self.active_connections:
            self.active_connections[meeting_id] = []
        self.active_connections[meeting_id].append(websocket)

    def disconnect(self, websocket: WebSocket, meeting_id: str) -> None:
        """Remove WebSocket connection."""
        if meeting_id in self.active_connections:
            self.active_connections[meeting_id].remove(websocket)
            if not self.active_connections[meeting_id]:
                del self.active_connections[meeting_id]

    async def broadcast(self, meeting_id: str, message: dict) -> None:
        """Broadcast message to all clients subscribed to a meeting."""
        if meeting_id in self.active_connections:
            message_json = json.dumps(message)
            for connection in self.active_connections[meeting_id]:
                await connection.send_text(message_json)

    async def send_event(self, meeting_id: str, event_type: str, data: dict) -> None:
        """Send formatted event to all meeting subscribers."""
        await self.broadcast(meeting_id, {"type": event_type, "data": data})
