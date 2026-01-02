"""Audio chunk schemas."""

from datetime import datetime

from pydantic import BaseModel


class AudioChunkBase(BaseModel):
    """Base audio chunk schema."""

    chunk_number: int
    duration_seconds: float


class AudioChunkCreate(AudioChunkBase):
    """Schema for creating audio chunk."""

    pass


class AudioChunkResponse(AudioChunkBase):
    """Schema for audio chunk response."""

    id: str
    meeting_id: str
    created_at: datetime
    transcription: str | None
    transcribed_at: datetime | None

    class Config:
        """Pydantic config."""

        from_attributes = True
