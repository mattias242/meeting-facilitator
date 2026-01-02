"""Test API endpoints with TDD approach."""

import json
import pytest
from fastapi.testclient import TestClient


class TestMeetingsAPI:
    """Test suite for meetings API endpoints."""

    def test_create_meeting_success(self, client: TestClient, sample_idoarrt_markdown):
        """Test successful meeting creation."""
        # Given
        payload = {"idoarrt_markdown": sample_idoarrt_markdown}
        
        # When
        response = client.post("/api/v1/meetings", json=payload)
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "meeting" in data
        assert data["meeting"]["intent"] == "Testa mötesfacilitering"
        assert data["meeting"]["status"] == "preparation"

    def test_create_meeting_invalid_markdown_fails(self, client: TestClient):
        """Test meeting creation with invalid markdown fails."""
        # Given
        payload = {"idoarrt_markdown": "invalid content"}
        
        # When
        response = client.post("/api/v1/meetings", json=payload)
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "validation_errors" in data
        assert len(data["validation_errors"]) > 0

    def test_get_meeting_success(self, client: TestClient, sample_idoarrt_markdown):
        """Test successful meeting retrieval."""
        # Given
        create_response = client.post("/api/v1/meetings", json={"idoarrt_markdown": sample_idoarrt_markdown})
        meeting_id = create_response.json()["meeting"]["id"]
        
        # When
        response = client.get(f"/api/v1/meetings/{meeting_id}")
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == meeting_id
        assert data["intent"] == "Testa mötesfacilitering"

    def test_get_nonexistent_meeting_returns_404(self, client: TestClient):
        """Test getting non-existent meeting returns 404."""
        # When
        response = client.get("/api/v1/meetings/nonexistent")
        
        # Then
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_start_meeting_success(self, client: TestClient, sample_idoarrt_markdown):
        """Test successful meeting start."""
        # Given
        create_response = client.post("/api/v1/meetings", json={"idoarrt_markdown": sample_idoarrt_markdown})
        meeting_id = create_response.json()["meeting"]["id"]
        
        # When
        response = client.patch(f"/api/v1/meetings/{meeting_id}/start")
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert "started_at" in data

    def test_start_already_started_meeting_fails(self, client: TestClient, sample_idoarrt_markdown):
        """Test starting already started meeting fails."""
        # Given
        create_response = client.post("/api/v1/meetings", json={"idoarrt_markdown": sample_idoarrt_markdown})
        meeting_id = create_response.json()["meeting"]["id"]
        client.patch(f"/api/v1/meetings/{meeting_id}/start")
        
        # When
        response = client.patch(f"/api/v1/meetings/{meeting_id}/start")
        
        # Then
        assert response.status_code == 400
        assert "already started" in response.json()["detail"].lower()

    def test_end_meeting_success(self, client: TestClient, sample_idoarrt_markdown):
        """Test successful meeting end."""
        # Given
        create_response = client.post("/api/v1/meetings", json={"idoarrt_markdown": sample_idoarrt_markdown})
        meeting_id = create_response.json()["meeting"]["id"]
        client.patch(f"/api/v1/meetings/{meeting_id}/start")
        
        # When
        response = client.patch(f"/api/v1/meetings/{meeting_id}/end")
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert "ended_at" in data

    def test_end_nonexistent_meeting_returns_404(self, client: TestClient):
        """Test ending non-existent meeting returns 404."""
        # When
        response = client.patch("/api/v1/meetings/nonexistent/end")
        
        # Then
        assert response.status_code == 404

    def test_extend_meeting_success(self, client: TestClient, sample_idoarrt_markdown):
        """Test successful meeting time extension."""
        # Given
        create_response = client.post("/api/v1/meetings", json={"idoarrt_markdown": sample_idoarrt_markdown})
        meeting_id = create_response.json()["meeting"]["id"]
        client.patch(f"/api/v1/meetings/{meeting_id}/start")
        
        # When
        response = client.patch(f"/api/v1/meetings/{meeting_id}/extend", json={"seconds": 300})
        
        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["time_extensions_seconds"] == 300

    def test_extend_inactive_meeting_fails(self, client: TestClient, sample_idoarrt_markdown):
        """Test extending inactive meeting fails."""
        # Given
        create_response = client.post("/api/v1/meetings", json={"idoarrt_markdown": sample_idoarrt_markdown})
        meeting_id = create_response.json()["meeting"]["id"]
        
        # When
        response = client.patch(f"/api/v1/meetings/{meeting_id}/extend", json={"seconds": 300})
        
        # Then
        assert response.status_code == 400
        assert "not active" in response.json()["detail"].lower()
