"""Meetings API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.meeting import MeetingCreate, MeetingResponse
from app.models.meeting import Meeting

router = APIRouter()


@router.post("/meetings", response_model=MeetingResponse)
async def create_meeting(
    meeting_data: MeetingCreate,
    db: Session = Depends(get_db)
) -> Meeting:
    """Create a new meeting from IDOARRT markdown."""
    # TODO: Implement IDOARRT parsing
    # For now, return a placeholder error
    raise HTTPException(status_code=501, detail="IDOARRT parsing not yet implemented")


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
