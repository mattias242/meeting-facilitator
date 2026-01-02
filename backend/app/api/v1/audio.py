"""Audio API endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.websocket import websocket_manager
from app.db.session import get_db
from app.models.meeting import AudioChunk, Meeting
from app.schemas.audio_chunk import AudioChunkResponse
from app.schemas.websocket_events import (
    InterventionQuestionEvent,
    InterventionTriggeredEvent,
    TranscriptionCompletedEvent,
    TranscriptionFailedEvent,
    TranscriptionStartedEvent,
    WebSocketEventType,
)
from app.services.audio_service import AudioService
from app.services.claude_service import get_claude_service
from app.services.transcription_service import TranscriptionService

# Initialize transcription service (lazy loads model on first use)
transcription_service = TranscriptionService()

router = APIRouter()


@router.post("/meetings/{meeting_id}/audio-chunks", response_model=AudioChunkResponse)
async def upload_audio_chunk(
    meeting_id: str,
    chunk_number: int = Form(...),
    duration_seconds: float = Form(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Any:
    """
    Upload an audio chunk for a meeting.

    Args:
        meeting_id: Meeting ID
        chunk_number: Sequential chunk number
        duration_seconds: Duration of this chunk in seconds
        audio_file: Audio file (WebM format)
        db: Database session

    Returns:
        Created audio chunk
    """
    # Verify meeting exists and is active
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting.status != "active":
        raise HTTPException(
            status_code=400, detail="Meeting must be active to upload audio"
        )

    # Read audio data
    audio_data = await audio_file.read()

    # Fix WebM duration metadata (required for HTML5 audio playback)
    try:
        fixed_audio_data = AudioService.fix_webm_duration(audio_data)
    except RuntimeError as e:
        # If ffmpeg fails, use original data (better than failing completely)
        print(f"Warning: Failed to fix WebM duration: {e}")
        fixed_audio_data = audio_data

    # Create audio chunk record
    audio_chunk = AudioChunk(
        meeting_id=meeting_id,
        chunk_number=chunk_number,
        audio_blob=fixed_audio_data,
        duration_seconds=duration_seconds,
    )

    db.add(audio_chunk)
    db.commit()
    db.refresh(audio_chunk)

    # Send WebSocket event: transcription started
    await websocket_manager.send_event(
        meeting_id,
        WebSocketEventType.TRANSCRIPTION_STARTED,
        TranscriptionStartedEvent(
            chunk_number=chunk_number, duration_seconds=duration_seconds
        ),
    )

    # Transcribe audio chunk (runs synchronously for now)
    try:
        print(f"Transcribing chunk {chunk_number}...")
        transcription = transcription_service.transcribe_audio(fixed_audio_data)

        # Save transcription
        from datetime import datetime

        audio_chunk.transcription = transcription  # type: ignore[assignment]
        audio_chunk.transcribed_at = datetime.utcnow()  # type: ignore[assignment]
        db.commit()
        db.refresh(audio_chunk)

        print(f"Chunk {chunk_number} transcribed: {transcription[:50]}...")

        # Send WebSocket event: transcription completed
        await websocket_manager.send_event(
            meeting_id,
            WebSocketEventType.TRANSCRIPTION_COMPLETED,
            TranscriptionCompletedEvent(
                chunk_number=chunk_number,
                transcription=transcription,
                duration_seconds=duration_seconds,
            ),
        )

        # Analyze transcription for triggers (only for active meetings)
        if meeting.status == "active":  # type: ignore[attr-defined]
            await analyze_and_send_interventions(
                meeting_id, meeting, transcription, db  # type: ignore[arg-type]
            )

    except Exception as e:
        print(f"Transcription failed: {e}")

        # Send WebSocket event: transcription failed
        await websocket_manager.send_event(
            meeting_id,
            WebSocketEventType.TRANSCRIPTION_FAILED,
            TranscriptionFailedEvent(chunk_number=chunk_number, error=str(e)),
        )
        # Don't fail the upload if transcription fails

    return audio_chunk


@router.get("/meetings/{meeting_id}/audio-chunks", response_model=list[AudioChunkResponse])
async def list_audio_chunks(
    meeting_id: str, db: Session = Depends(get_db)
) -> Any:
    """
    List all audio chunks for a meeting.

    Args:
        meeting_id: Meeting ID
        db: Database session

    Returns:
        List of audio chunks
    """
    # Verify meeting exists
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Get all audio chunks for this meeting
    chunks = (
        db.query(AudioChunk)
        .filter(AudioChunk.meeting_id == meeting_id)
        .order_by(AudioChunk.chunk_number)
        .all()
    )

    return chunks


@router.get("/audio-chunks/{chunk_id}/audio")
async def get_audio_chunk_blob(
    chunk_id: str, db: Session = Depends(get_db)
) -> Response:
    """
    Get audio blob for a specific chunk.

    Args:
        chunk_id: Audio chunk ID
        db: Database session

    Returns:
        Audio blob as WebM file
    """
    chunk = db.query(AudioChunk).filter(AudioChunk.id == chunk_id).first()
    if not chunk:
        raise HTTPException(status_code=404, detail="Audio chunk not found")

    return Response(
        content=chunk.audio_blob,
        media_type="audio/webm",
        headers={
            "Content-Disposition": f'inline; filename="chunk-{chunk.chunk_number}.webm"'
        },
    )


@router.post("/meetings/{meeting_id}/upload-recording")
async def upload_recording(
    meeting_id: str,
    chunk_duration_minutes: int = Form(2),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Upload a complete meeting recording and split it into chunks.

    This is a testing utility - upload a pre-recorded meeting audio file
    and it will be split into chunks as if it was recorded live.

    Args:
        meeting_id: Meeting ID
        chunk_duration_minutes: Duration of each chunk in minutes (default 2)
        audio_file: Audio file (any format - mp3, wav, m4a, etc.)
        db: Database session

    Returns:
        Summary of uploaded chunks
    """
    # Verify meeting exists
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Read audio file
    audio_data = await audio_file.read()

    try:
        # Split into chunks
        chunks_created = []
        for chunk_data in AudioService.split_audio_into_chunks(
            audio_data, chunk_duration_minutes
        ):
            # Create audio chunk record
            audio_chunk = AudioChunk(
                meeting_id=meeting_id,
                chunk_number=chunk_data.chunk_number,
                audio_blob=chunk_data.audio_data,
                duration_seconds=chunk_data.duration_seconds,
            )

            db.add(audio_chunk)
            db.flush()  # Get ID without committing

            # Send WebSocket event: transcription started
            await websocket_manager.send_event(
                meeting_id,
                WebSocketEventType.TRANSCRIPTION_STARTED,
                TranscriptionStartedEvent(
                    chunk_number=chunk_data.chunk_number,
                    duration_seconds=chunk_data.duration_seconds,
                ),
            )

            # Transcribe chunk
            try:
                print(f"Transcribing chunk {chunk_data.chunk_number}...")
                transcription = transcription_service.transcribe_audio(chunk_data.audio_data)
                from datetime import datetime

                audio_chunk.transcription = transcription  # type: ignore[assignment]
                audio_chunk.transcribed_at = datetime.utcnow()  # type: ignore[assignment]
                print(f"Chunk {chunk_data.chunk_number} transcribed")

                # Send WebSocket event: transcription completed
                await websocket_manager.send_event(
                    meeting_id,
                    WebSocketEventType.TRANSCRIPTION_COMPLETED,
                    TranscriptionCompletedEvent(
                        chunk_number=chunk_data.chunk_number,
                        transcription=transcription,
                        duration_seconds=chunk_data.duration_seconds,
                    ),
                )
            except Exception as e:
                print(f"Transcription failed for chunk {chunk_data.chunk_number}: {e}")

                # Send WebSocket event: transcription failed
                await websocket_manager.send_event(
                    meeting_id,
                    WebSocketEventType.TRANSCRIPTION_FAILED,
                    TranscriptionFailedEvent(
                        chunk_number=chunk_data.chunk_number, error=str(e)
                    ),
                )

            chunks_created.append(
                {
                    "chunk_number": chunk_data.chunk_number,
                    "duration_seconds": chunk_data.duration_seconds,
                    "size_bytes": len(chunk_data.audio_data),
                    "transcription": audio_chunk.transcription or "",
                }
            )

        # Commit all chunks
        db.commit()

        # Update meeting status to completed
        meeting.status = "completed"  # type: ignore[assignment]
        from datetime import datetime

        if not meeting.started_at:
            meeting.started_at = datetime.utcnow()  # type: ignore[assignment]
        meeting.ended_at = datetime.utcnow()  # type: ignore[assignment]
        db.commit()

        return {
            "success": True,
            "chunks_created": len(chunks_created),
            "chunks": chunks_created,
            "total_duration_seconds": sum(c["duration_seconds"] for c in chunks_created),
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to process audio: {str(e)}"
        ) from e
