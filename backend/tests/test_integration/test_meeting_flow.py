"""Integration tests for full meeting flow."""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import Base, get_db


# Integration test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def integration_client():
    """Create test client for integration tests."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


class TestMeetingFlowIntegration:
    """Integration tests for complete meeting workflow."""

    def test_full_meeting_lifecycle(self, integration_client):
        """Test complete meeting from creation to protocol generation."""
        # Step 1: Create meeting
        idoarrt_content = """# Test Integration Meeting

## Intent
Test complete integration flow

## Desired Outcomes
- Verify TDD implementation
- Test meeting lifecycle

## Agenda
- Setup (5 min)
- Recording (10 min)
- Analysis (5 min)

## Roles
- Facilitator: Test User
- Note Taker: AI

## Rules
- Follow TDD principles
- Test all components

## Time
20"""
        
        create_response = integration_client.post("/api/v1/meetings", json={
            "idoarrt_markdown": idoarrt_content
        })
        assert create_response.status_code == 200
        meeting_data = create_response.json()
        assert meeting_data["success"] is True
        meeting_id = meeting_data["meeting"]["id"]
        
        # Step 2: Start meeting
        start_response = integration_client.patch(f"/api/v1/meetings/{meeting_id}/start")
        assert start_response.status_code == 200
        assert start_response.json()["status"] == "active"
        
        # Step 3: Upload audio chunk (mock)
        mock_audio = b"fake audio data"
        files = {"audio_file": ("test.webm", mock_audio, "audio/webm")}
        data = {
            "chunk_number": 1,
            "duration_seconds": 120.0
        }
        
        upload_response = integration_client.post(
            f"/api/v1/meetings/{meeting_id}/audio-chunks",
            files=files,
            data=data
        )
        assert upload_response.status_code == 200
        chunk_data = upload_response.json()
        assert chunk_data["chunk_number"] == 1
        
        # Step 4: Get audio chunks
        chunks_response = integration_client.get(f"/api/v1/meetings/{meeting_id}/audio-chunks")
        assert chunks_response.status_code == 200
        chunks = chunks_response.json()
        assert len(chunks) == 1
        
        # Step 5: End meeting
        end_response = integration_client.patch(f"/api/v1/meetings/{meeting_id}/end")
        assert end_response.status_code == 200
        assert end_response.json()["status"] == "completed"
        
        # Step 6: Generate protocol
        protocol_response = integration_client.post(f"/api/v1/meetings/{meeting_id}/protocol/generate")
        assert protocol_response.status_code == 200
        
        # Step 7: Get protocol
        get_protocol_response = integration_client.get(f"/api/v1/meetings/{meeting_id}/protocol")
        assert get_protocol_response.status_code == 200
        protocol = get_protocol_response.json()
        assert "full_transcription" in protocol
        assert "markdown_content" in protocol

    def test_meeting_validation_errors(self, integration_client):
        """Test meeting creation with validation errors."""
        invalid_idoarrt = """# Invalid Meeting
## Intent
"""
        
        response = integration_client.post("/api/v1/meetings", json={
            "idoarrt_markdown": invalid_idoarrt
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert len(data["validation_errors"]) > 0

    def test_audio_upload_validation(self, integration_client):
        """Test audio upload validation."""
        # First create and start a meeting
        create_response = integration_client.post("/api/v1/meetings", json={
            "idoarrt_markdown": """# Test
## Intent
Test
## Desired Outcomes
- Test
## Agenda
- Test (5 min)
## Roles
- Test: User
## Rules
- Test
## Time
5"""
        })
        meeting_id = create_response.json()["meeting"]["id"]
        integration_client.patch(f"/api/v1/meetings/{meeting_id}/start")
        
        # Test upload to non-existent meeting
        response = integration_client.post("/api/v1/meetings/nonexistent/audio-chunks")
        assert response.status_code == 404
        
        # Test upload to inactive meeting
        integration_client.patch(f"/api/v1/meetings/{meeting_id}/end")
        response = integration_client.post(f"/api/v1/meetings/{meeting_id}/audio-chunks")
        assert response.status_code == 400
        assert "active" in response.json()["detail"].lower()

    def test_websocket_connection_flow(self, integration_client):
        """Test WebSocket connection and message flow."""
        # Create meeting
        create_response = integration_client.post("/api/v1/meetings", json={
            "idoarrt_markdown": """# WS Test
## Intent
Test WebSocket
## Desired Outcomes
- Test WS connection
## Agenda
- Test (5 min)
## Roles
- Test: User
## Rules
- Test
## Time
5"""
        })
        meeting_id = create_response.json()["meeting"]["id"]
        
        # Test WebSocket connection (using TestClient's websocket support)
        with integration_client.websocket_connect(f"/ws/meetings/{meeting_id}") as websocket:
            # Send ping message
            websocket.send_json({"type": "ping", "timestamp": "123456"})
            
            # Receive pong response
            data = websocket.receive_json()
            assert data["type"] == "pong"
            assert data["timestamp"] == "123456"
            
            # Send subscription message
            websocket.send_json({"type": "subscribe"})
            
            # Connection should remain open
            assert websocket.websocket is not None
