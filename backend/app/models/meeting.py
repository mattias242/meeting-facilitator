"""Meeting database models."""

from datetime import datetime
from typing import List
import uuid

from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, Float, LargeBinary, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.db.session import Base


class Meeting(Base):
    """Meeting model with IDOARRT framework."""

    __tablename__ = "meetings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # IDOARRT data
    intent = Column(Text, nullable=False)
    desired_outcomes = Column(JSON, nullable=False)  # List of outcome strings
    agenda = Column(JSON, nullable=False)  # List of {topic, duration_minutes}
    roles = Column(JSON, nullable=False)  # Dict of role: person_name
    rules = Column(JSON, nullable=False)  # List of rule strings
    total_duration_minutes = Column(Integer, nullable=False)

    # Meeting state
    status = Column(String, default="preparation", nullable=False)  # preparation|active|completed
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    time_extensions_seconds = Column(Integer, default=0, nullable=False)

    # Relationships
    audio_chunks = relationship("AudioChunk", back_populates="meeting", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="meeting", cascade="all, delete-orphan")
    protocol = relationship("Protocol", back_populates="meeting", uselist=False, cascade="all, delete-orphan")


class AudioChunk(Base):
    """Audio chunk with transcription."""

    __tablename__ = "audio_chunks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    chunk_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Audio data
    audio_blob = Column(LargeBinary, nullable=False)  # WebM/Opus format
    duration_seconds = Column(Float, nullable=False)

    # Transcription
    transcription = Column(Text, nullable=True)
    transcribed_at = Column(DateTime, nullable=True)

    # Relationships
    meeting = relationship("Meeting", back_populates="audio_chunks")

    __table_args__ = (
        Index('ix_audio_chunks_meeting_chunk', 'meeting_id', 'chunk_number'),
    )


class Intervention(Base):
    """Meeting intervention (coaching question or advice)."""

    __tablename__ = "interventions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Intervention details
    intervention_type = Column(String, nullable=False)  # time_warning|goal_deviation|perspective_gap|complexity_mistake
    trigger_context = Column(JSON, nullable=True)  # What triggered this intervention

    # Assistant output
    question = Column(Text, nullable=True)
    coaching_note = Column(Text, nullable=True)

    # State
    displayed = Column(Boolean, default=False, nullable=False)
    dismissed_at = Column(DateTime, nullable=True)

    # Relationships
    meeting = relationship("Meeting", back_populates="interventions")

    __table_args__ = (
        Index('ix_interventions_meeting', 'meeting_id', 'created_at'),
    )


class Protocol(Base):
    """Meeting protocol and summary."""

    __tablename__ = "protocols"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    meeting_id = Column(String, ForeignKey("meetings.id"), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Protocol content
    full_transcription = Column(Text, nullable=False)
    agenda_summary = Column(JSON, nullable=True)  # Summary per agenda item
    goal_assessment = Column(JSON, nullable=True)  # For each desired outcome
    key_decisions = Column(JSON, nullable=True)
    action_items = Column(JSON, nullable=True)

    # Export
    markdown_content = Column(Text, nullable=False)

    # Relationships
    meeting = relationship("Meeting", back_populates="protocol")
