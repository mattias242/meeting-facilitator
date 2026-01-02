"""File upload security utilities."""

import os
import magic
from typing import Tuple
from fastapi import HTTPException, UploadFile


class FileUploadSecurity:
    """Security utilities for file uploads."""
    
    # Allowed MIME types for audio files
    ALLOWED_AUDIO_TYPES = {
        'audio/webm',
        'audio/ogg',
        'audio/wav',
        'audio/x-wav',  # python-magic reports WAV as audio/x-wav
        'audio/mp3',
        'audio/mpeg',
        'audio/m4a'
    }
    
    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    @classmethod
    def validate_audio_file(cls, file: UploadFile) -> Tuple[bool, str]:
        """
        Validate uploaded audio file.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if file.size and file.size > cls.MAX_FILE_SIZE:
            return False, f"File too large. Maximum size is {cls.MAX_FILE_SIZE // (1024*1024)}MB"
        
        # Check file extension
        if not file.filename:
            return False, "No filename provided"
        
        allowed_extensions = {'.webm', '.ogg', '.wav', '.mp3', '.m4a'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return False, f"File extension {file_ext} not allowed"
        
        return True, ""
    
    @classmethod
    def validate_audio_content(cls, file_content: bytes) -> Tuple[bool, str]:
        """
        Validate actual file content using python-magic.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Detect MIME type from file content
            mime_type = magic.from_buffer(file_content, mime=True)
            
            if mime_type not in cls.ALLOWED_AUDIO_TYPES:
                return False, f"File type {mime_type} not allowed"
            
            return True, ""
            
        except Exception as e:
            return False, f"Error validating file content: {str(e)}"
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename to prevent path traversal attacks."""
        # Remove path separators and dangerous characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        sanitized = ''.join(c for c in filename if c in safe_chars)
        
        # Ensure filename doesn't start with dot or dash
        while sanitized.startswith(('.', '-')):
            sanitized = sanitized[1:]
        
        return sanitized or "upload"
