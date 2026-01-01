"""Pydantic schemas for meetings and related entities."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AgendaItem(BaseModel):
    """Single agenda item."""
    topic: str
    duration_minutes: int


class IDOARRTData(BaseModel):
    """Parsed IDOARRT data."""
    intent: str
    desired_outcomes: list[str]
    agenda: list[AgendaItem]
    roles: dict[str, str]
    rules: list[str]
    total_duration_minutes: int


class MeetingCreate(BaseModel):
    """Create meeting from IDOARRT markdown."""
    idoarrt_markdown: str


class MeetingResponse(BaseModel):
    """Meeting response."""
    id: str
    created_at: datetime
    intent: str
    desired_outcomes: list[str]
    agenda: list[dict[str, Any]]
    roles: dict[str, str]
    rules: list[str]
    total_duration_minutes: int
    status: str
    started_at: datetime | None = None
    ended_at: datetime | None = None
    time_extensions_seconds: int

    class Config:
        from_attributes = True


class MeetingUpdate(BaseModel):
    """Update meeting status."""
    status: str | None = None
    time_extensions_seconds: int | None = None


class AudioChunkUpload(BaseModel):
    """Audio chunk upload metadata."""
    chunk_number: int
    duration_seconds: float


class InterventionResponse(BaseModel):
    """Intervention response."""
    id: str
    created_at: datetime
    intervention_type: str
    question: str | None = None
    coaching_note: str | None = None
    trigger_context: dict[str, Any] | None = None

    class Config:
        from_attributes = True


class ProtocolResponse(BaseModel):
    """Protocol response."""
    id: str
    created_at: datetime
    full_transcription: str
    agenda_summary: dict[str, Any] | None = None
    goal_assessment: dict[str, Any] | None = None
    key_decisions: list[str] | None = None
    action_items: list[dict[str, str]] | None = None
    markdown_content: str

    class Config:
        from_attributes = True
