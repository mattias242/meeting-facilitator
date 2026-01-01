"""Pydantic schemas for meetings and related entities."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class AgendaItem(BaseModel):
    """Single agenda item."""
    topic: str
    duration_minutes: int


class IDOARRTData(BaseModel):
    """Parsed IDOARRT data."""
    intent: str
    desired_outcomes: List[str]
    agenda: List[AgendaItem]
    roles: Dict[str, str]
    rules: List[str]
    total_duration_minutes: int


class MeetingCreate(BaseModel):
    """Create meeting from IDOARRT markdown."""
    idoarrt_markdown: str


class MeetingResponse(BaseModel):
    """Meeting response."""
    id: str
    created_at: datetime
    intent: str
    desired_outcomes: List[str]
    agenda: List[Dict[str, Any]]
    roles: Dict[str, str]
    rules: List[str]
    total_duration_minutes: int
    status: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    time_extensions_seconds: int

    class Config:
        from_attributes = True


class MeetingUpdate(BaseModel):
    """Update meeting status."""
    status: Optional[str] = None
    time_extensions_seconds: Optional[int] = None


class AudioChunkUpload(BaseModel):
    """Audio chunk upload metadata."""
    chunk_number: int
    duration_seconds: float


class InterventionResponse(BaseModel):
    """Intervention response."""
    id: str
    created_at: datetime
    intervention_type: str
    question: Optional[str] = None
    coaching_note: Optional[str] = None
    trigger_context: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ProtocolResponse(BaseModel):
    """Protocol response."""
    id: str
    created_at: datetime
    full_transcription: str
    agenda_summary: Optional[Dict[str, Any]] = None
    goal_assessment: Optional[Dict[str, Any]] = None
    key_decisions: Optional[List[str]] = None
    action_items: Optional[List[Dict[str, str]]] = None
    markdown_content: str

    class Config:
        from_attributes = True
