"""WebSocket event schemas for real-time meeting updates."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class WebSocketEventType(str, Enum):
    """Types of WebSocket events."""

    # Transcription events
    TRANSCRIPTION_STARTED = "transcription_started"
    TRANSCRIPTION_COMPLETED = "transcription_completed"
    TRANSCRIPTION_FAILED = "transcription_failed"

    # Intervention events
    INTERVENTION_TRIGGERED = "intervention_triggered"
    INTERVENTION_QUESTION = "intervention_question"

    # Meeting status events
    MEETING_STARTED = "meeting_started"
    MEETING_EXTENDED = "meeting_extended"
    MEETING_ENDED = "meeting_ended"

    # Time warnings
    TIME_WARNING = "time_warning"

    # Error events
    ERROR = "error"


class TranscriptionStartedEvent(BaseModel):
    """Event sent when transcription starts."""

    chunk_number: int
    duration_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TranscriptionCompletedEvent(BaseModel):
    """Event sent when transcription completes."""

    chunk_number: int
    transcription: str
    duration_seconds: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TranscriptionFailedEvent(BaseModel):
    """Event sent when transcription fails."""

    chunk_number: int
    error: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class InterventionType(str, Enum):
    """Types of interventions."""

    TIME_WARNING = "time_warning"
    GOAL_DEVIATION = "goal_deviation"
    PERSPECTIVE_GAP = "perspective_gap"
    COMPLEXITY_MISTAKE = "complexity_mistake"


class InterventionTriggeredEvent(BaseModel):
    """Event sent when an intervention is triggered."""

    intervention_type: InterventionType
    reason: str
    context: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class InterventionQuestionEvent(BaseModel):
    """Event sent with a facilitation question."""

    intervention_type: InterventionType
    question: str
    context: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MeetingStartedEvent(BaseModel):
    """Event sent when meeting starts."""

    meeting_id: str
    started_at: datetime
    total_duration_minutes: int


class MeetingExtendedEvent(BaseModel):
    """Event sent when meeting time is extended."""

    meeting_id: str
    extended_by_seconds: int
    new_end_time: datetime


class MeetingEndedEvent(BaseModel):
    """Event sent when meeting ends."""

    meeting_id: str
    ended_at: datetime
    total_duration_minutes: int


class TimeWarningEvent(BaseModel):
    """Event sent for time warnings."""

    percentage_complete: int  # e.g., 50, 75
    remaining_minutes: int
    message: str


class ErrorEvent(BaseModel):
    """Event sent when an error occurs."""

    error: str
    details: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WebSocketEvent(BaseModel):
    """Generic WebSocket event wrapper."""

    type: WebSocketEventType
    data: dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
