"""Logging middleware for FastAPI requests."""

import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging_config import log_api_request, get_logger

logger = get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Store request ID in state for other middleware to use
        request.state.request_id = request_id
        
        # Get start time
        start_time = time.time()
        
        # Extract user info if available (from JWT token)
        user_id = None
        auth_header = request.headers.get("authorization")
        if auth_header:
            try:
                # Extract user ID from JWT token (simplified)
                # In production, you'd decode the JWT properly
                user_id = "extracted_from_jwt"  # Placeholder
            except Exception:
                pass
        
        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path} - "
            f"ID: {request_id} - User: {user_id or 'anonymous'} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} - "
                f"ID: {request_id} - Status: {response.status_code} - "
                f"Duration: {duration_ms:.2f}ms - User: {user_id or 'anonymous'}"
            )
            
            # Log to specialized API logger
            log_api_request(
                method=request.method,
                path=request.url.path,
                user_id=user_id,
                status_code=response.status_code,
                duration_ms=duration_ms
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Log error
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed: {request.method} {request.url.path} - "
                f"ID: {request_id} - Error: {str(e)} - "
                f"Duration: {duration_ms:.2f}ms - User: {user_id or 'anonymous'}"
            )
            raise
