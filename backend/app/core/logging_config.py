"""Logging configuration for Meeting Facilitator backend."""

import logging
import os
from datetime import datetime
from pathlib import Path

# Create logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
def setup_logging():
    """Setup comprehensive logging for the application."""
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create handlers
    # 1. Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # 2. General application log
    app_handler = logging.FileHandler(LOGS_DIR / "app.log", encoding='utf-8')
    app_handler.setLevel(logging.DEBUG)
    app_handler.setFormatter(detailed_formatter)
    
    # 3. Error log for errors and exceptions
    error_handler = logging.FileHandler(LOGS_DIR / "errors.log", encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # 4. Security log for authentication and authorization events
    security_handler = logging.FileHandler(LOGS_DIR / "security.log", encoding='utf-8')
    security_handler.setLevel(logging.INFO)
    security_handler.setFormatter(detailed_formatter)
    
    # 5. API request log
    api_handler = logging.FileHandler(LOGS_DIR / "api.log", encoding='utf-8')
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(detailed_formatter)
    
    # 6. Audio processing log
    audio_handler = logging.FileHandler(LOGS_DIR / "audio.log", encoding='utf-8')
    audio_handler.setLevel(logging.INFO)
    audio_handler.setFormatter(detailed_formatter)
    
    # 7. Claude API log
    claude_handler = logging.FileHandler(LOGS_DIR / "claude.log", encoding='utf-8')
    claude_handler.setLevel(logging.INFO)
    claude_handler.setFormatter(detailed_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    
    # Configure specific loggers
    loggers_config = {
        'app.api': [api_handler],
        'app.core.auth': [security_handler],
        'app.services.audio': [audio_handler],
        'app.services.claude': [claude_handler],
        'app.services.transcription': [audio_handler],
        'uvicorn': [console_handler, app_handler],
        'fastapi': [console_handler, app_handler],
    }
    
    for logger_name, handlers in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        for handler in handlers:
            logger.addHandler(handler)
    
    # Log startup
    app_logger = logging.getLogger("app")
    app_logger.info("=" * 50)
    app_logger.info("Meeting Facilitator Backend Starting")
    app_logger.info(f"Log directory: {LOGS_DIR.absolute()}")
    app_logger.info(f"Environment: {os.getenv('ENV', 'development')}")
    app_logger.info("=" * 50)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)

# Security logging helpers
def log_security_event(event_type: str, details: dict, user_id: str = None):
    """Log security-related events."""
    security_logger = logging.getLogger("app.core.auth")
    security_logger.info(f"SECURITY_EVENT: {event_type} - User: {user_id or 'anonymous'} - Details: {details}")

def log_api_request(method: str, path: str, user_id: str = None, status_code: int = None, duration_ms: float = None):
    """Log API requests."""
    api_logger = logging.getLogger("app.api")
    api_logger.info(f"API_REQUEST: {method} {path} - User: {user_id or 'anonymous'} - Status: {status_code} - Duration: {duration_ms}ms")

def log_audio_event(event_type: str, meeting_id: str, chunk_number: int = None, details: dict = None):
    """Log audio processing events."""
    audio_logger = logging.getLogger("app.services.audio")
    audio_logger.info(f"AUDIO_EVENT: {event_type} - Meeting: {meeting_id} - Chunk: {chunk_number} - Details: {details or {}}")

def log_claude_event(event_type: str, meeting_id: str, details: dict = None):
    """Log Claude API events."""
    claude_logger = logging.getLogger("app.services.claude")
    claude_logger.info(f"CLAUDE_EVENT: {event_type} - Meeting: {meeting_id} - Details: {details or {}}")
