"""Main FastAPI application for Meeting Facilitator."""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import audio, auth, meetings, protocols
from app.core.websocket import websocket_manager
from app.db.session import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Meeting Facilitator API",
    description="AI-powered meeting facilitation using IDOARRT and GROW model",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(meetings.router, prefix="/api/v1", tags=["meetings"])
app.include_router(audio.router, prefix="/api/v1", tags=["audio"])
app.include_router(protocols.router, prefix="/api/v1", tags=["protocols"])


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "Meeting Facilitator API"}


@app.websocket("/ws/meetings/{meeting_id}")
async def websocket_endpoint(websocket: WebSocket, meeting_id: str, token: str = None) -> None:
    """WebSocket endpoint for real-time meeting updates with authentication."""
    # Verify JWT token if provided
    if token:
        try:
            from app.core.auth import verify_token
            payload = verify_token(type('Credentials', (), {'credentials': token})())
            # Token is valid, proceed with connection
        except Exception:
            await websocket.close(code=1008, reason="Invalid authentication token")
            return
    else:
        # For development, allow connections without token
        # TODO: Remove this in production
        pass
    
    await websocket_manager.connect(websocket, meeting_id)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming messages
            if data.get("type") == "subscribe":
                # Client is subscribing to meeting events
                pass
            elif data.get("type") == "ping":
                # Heartbeat
                await websocket.send_json({"type": "pong", "timestamp": data.get("timestamp")})
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, meeting_id)
