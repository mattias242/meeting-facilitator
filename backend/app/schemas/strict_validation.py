"""Enhanced Pydantic schemas with strict validation."""

from typing import Any
from pydantic import BaseModel, Field, validator
import re


class StrictMeetingCreate(BaseModel):
    """Strict meeting creation schema with validation."""
    
    idoarrt_markdown: str = Field(
        ..., 
        min_length=50, 
        max_length=10000,
        description="IDOARRT markdown content"
    )
    
    @validator('idoarrt_markdown')
    def validate_idoarrt_format(cls, v):
        """Validate IDOARRT markdown has required sections."""
        required_sections = ['Intent', 'Desired Outcomes', 'Agenda', 'Roles', 'Rules', 'Time']
        
        # Check for required sections using # Header format
        for section in required_sections:
            pattern = rf'^#\s+{re.escape(section)}\s*$'
            if not re.search(pattern, v, re.MULTILINE | re.IGNORECASE):
                raise ValueError(f'Missing required section: {section}')
        
        # Validate Time section format
        time_pattern = r'#\s+Time\s*.*Total:\s*(\d+)\s*(?:minutes?|min)'
        if not re.search(time_pattern, v, re.MULTILINE | re.IGNORECASE):
            raise ValueError('Time section must contain "Total: XX minutes"')
        
        # Validate Agenda has numbered items with time
        agenda_pattern = r'#\s+Agenda\s*.*(\d+\.\s+.+\(\s*\d+\s*min\))'
        if not re.search(agenda_pattern, v, re.MULTILINE | re.IGNORECASE):
            raise ValueError('Agenda must have numbered items with time allocation')
        
        return v


class StrictAudioChunkUpload(BaseModel):
    """Strict audio chunk upload validation."""
    
    chunk_number: int = Field(..., ge=1, le=1000)
    duration_seconds: float = Field(..., ge=1.0, le=600.0)  # Max 10 minutes per chunk


class StrictMeetingTimeExtension(BaseModel):
    """Strict meeting time extension validation."""
    
    seconds: int = Field(..., ge=60, le=3600)  # 1 minute to 1 hour
