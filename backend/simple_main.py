"""Simple FastAPI app for testing without security."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create simple app
app = FastAPI(
    title="Meeting Facilitator API",
    description="Simple version for testing",
    version="0.1.0-simple",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "service": "Meeting Facilitator API"}

# Import and include original routes without security
try:
    from app.api.v1 import meetings, audio, protocols
    app.include_router(meetings.router, prefix="/api/v1", tags=["meetings"])
    app.include_router(audio.router, prefix="/api/v1", tags=["audio"])
    app.include_router(protocols.router, prefix="/api/v1", tags=["protocols"])
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
