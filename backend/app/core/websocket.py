"""WebSocket connection manager for real-time meeting updates."""

import json
import logging
from typing import Any

from fastapi import WebSocket
from pydantic import BaseModel

from app.schemas.websocket_events import WebSocketEvent, WebSocketEventType

logger = logging.getLogger(__name__)


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
        logger.info(f"WebSocket connected for meeting {meeting_id}")

    def disconnect(self, websocket: WebSocket, meeting_id: str) -> None:
        """Remove WebSocket connection."""
        if meeting_id in self.active_connections:
            if websocket in self.active_connections[meeting_id]:
                self.active_connections[meeting_id].remove(websocket)
            if not self.active_connections[meeting_id]:
                del self.active_connections[meeting_id]
        logger.info(f"WebSocket disconnected for meeting {meeting_id}")

    async def broadcast(self, meeting_id: str, message: dict[str, Any]) -> None:
        """Broadcast message to all clients subscribed to a meeting."""
        if meeting_id in self.active_connections:
            message_json = json.dumps(message, default=str)
            disconnected = []
            for connection in self.active_connections[meeting_id]:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Error sending message to WebSocket: {e}")
                    disconnected.append(connection)

            # Clean up disconnected clients
            for connection in disconnected:
                self.disconnect(connection, meeting_id)

    async def send_event(
        self, meeting_id: str, event_type: WebSocketEventType, data: BaseModel | dict[str, Any]
    ) -> None:
        """
        Send typed event to all meeting subscribers.

        Args:
            meeting_id: Meeting ID
            event_type: Type of event
            data: Event data (Pydantic model or dict)
        """
        # Convert Pydantic model to dict if needed
        data_dict = data.model_dump() if isinstance(data, BaseModel) else data

        event = WebSocketEvent(type=event_type, data=data_dict)
        await self.broadcast(meeting_id, event.model_dump())
        logger.debug(f"Sent {event_type} event to meeting {meeting_id}")


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
