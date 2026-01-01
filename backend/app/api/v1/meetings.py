"""Meetings API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.session import get_db
from app.schemas.meeting import MeetingCreate, MeetingResponse
from app.models.meeting import Meeting
from app.services.idoarrt_service import IDOARRTService, IDOARRTParseError

router = APIRouter()
idoarrt_service = IDOARRTService()


@router.post("/meetings", response_model=Dict[str, Any])
async def create_meeting(
    meeting_data: MeetingCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a new meeting from IDOARRT markdown.

    Returns the created meeting with validation status.
    """
    try:
        # Parse IDOARRT markdown
        parsed_data = idoarrt_service.parse_idoarrt(meeting_data.idoarrt_markdown)

        # Validate parsed data
        validation_errors = idoarrt_service.validate_idoarrt(parsed_data)

        if validation_errors:
            return {
                "success": False,
                "validation_errors": validation_errors,
                "parsed_idoarrt": parsed_data,
            }

        # Create meeting in database
        meeting = Meeting(
            intent=parsed_data["intent"],
            desired_outcomes=parsed_data["desired_outcomes"],
            agenda=parsed_data["agenda"],
            roles=parsed_data["roles"],
            rules=parsed_data["rules"],
            total_duration_minutes=parsed_data["total_duration_minutes"],
            status="preparation",
        )

        db.add(meeting)
        db.commit()
        db.refresh(meeting)

        return {
            "success": True,
            "meeting": {
                "id": meeting.id,
                "created_at": meeting.created_at.isoformat(),
                "intent": meeting.intent,
                "desired_outcomes": meeting.desired_outcomes,
                "agenda": meeting.agenda,
                "roles": meeting.roles,
                "rules": meeting.rules,
                "total_duration_minutes": meeting.total_duration_minutes,
                "status": meeting.status,
                "started_at": meeting.started_at.isoformat() if meeting.started_at else None,
                "ended_at": meeting.ended_at.isoformat() if meeting.ended_at else None,
                "time_extensions_seconds": meeting.time_extensions_seconds,
            },
            "validation_errors": [],
            "parsed_idoarrt": parsed_data,
        }

    except IDOARRTParseError as e:
        return {
            "success": False,
            "validation_errors": [str(e)],
            "parsed_idoarrt": None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/meetings/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: str,
    db: Session = Depends(get_db)
) -> Meeting:
    """Get meeting by ID."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.patch("/meetings/{meeting_id}/start")
async def start_meeting(
    meeting_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Start a meeting."""
    from datetime import datetime

    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting.status != "preparation":
        raise HTTPException(status_code=400, detail="Meeting already started or completed")

    meeting.status = "active"
    meeting.started_at = datetime.utcnow()
    db.commit()
    db.refresh(meeting)

    return {
        "id": meeting.id,
        "status": meeting.status,
        "started_at": meeting.started_at.isoformat(),
    }


@router.patch("/meetings/{meeting_id}/end")
async def end_meeting(
    meeting_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """End a meeting."""
    from datetime import datetime

    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting.status != "active":
        raise HTTPException(status_code=400, detail="Meeting not active")

    meeting.status = "completed"
    meeting.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(meeting)

    return {
        "id": meeting.id,
        "status": meeting.status,
        "ended_at": meeting.ended_at.isoformat(),
    }


@router.patch("/meetings/{meeting_id}/extend")
async def extend_meeting(
    meeting_id: str,
    seconds: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Extend meeting time."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting.status != "active":
        raise HTTPException(status_code=400, detail="Meeting not active")

    meeting.time_extensions_seconds += seconds
    db.commit()
    db.refresh(meeting)

    return {
        "id": meeting.id,
        "time_extensions_seconds": meeting.time_extensions_seconds,
    }
