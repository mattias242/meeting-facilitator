"""Test IDOARRT service with TDD approach."""

import pytest
from app.services.idoarrt_service import IDOARRTService, IDOARRTParseError


class TestIDOARRTService:
    """Test suite for IDOARRT parsing and validation."""

    def setup_method(self):
        """Set up test instance."""
        self.service = IDOARRTService()

    def test_parse_valid_idoarrt_success(self, sample_idoarrt_markdown):
        """Test parsing valid IDOARRT markdown."""
        # When
        result = self.service.parse_idoarrt(sample_idoarrt_markdown)
        
        # Then
        assert result["intent"] == "Testa mötesfacilitering"
        assert len(result["desired_outcomes"]) == 2
        assert "Testa systemet" in result["desired_outcomes"]
        assert len(result["agenda"]) == 3
        assert result["total_duration_minutes"] == 30
        assert "Facilitator" in result["roles"]
        assert result["roles"]["Facilitator"] == "Anna"

    def test_parse_empty_markdown_raises_error(self):
        """Test that empty markdown raises parsing error."""
        # When/Then
        with pytest.raises(IDOARRTParseError, match="No content found"):
            self.service.parse_idoarrt("")

    def test_parse_missing_intent_raises_error(self):
        """Test that missing intent raises validation error."""
        # Given
        markdown = """# Test
## Desired Outcomes
- Test
"""
        
        # When/Then
        with pytest.raises(IDOARRTParseError, match="Intent section is required"):
            self.service.parse_idoarrt(markdown)

    def test_parse_invalid_time_format_raises_error(self):
        """Test that invalid time format raises error."""
        # Given
        markdown = """# Test
## Intent
Test
## Time
invalid
"""
        
        # When/Then
        with pytest.raises(IDOARRTParseError, match="Invalid time format"):
            self.service.parse_idoarrt(markdown)

    def test_validate_complete_idoarrt_passes(self, sample_idoarrt_markdown):
        """Test validation of complete IDOARRT passes."""
        # Given
        parsed = self.service.parse_idoarrt(sample_idoarrt_markdown)
        
        # When
        errors = self.service.validate_idoarrt(parsed)
        
        # Then
        assert errors == []

    def test_validate_empty_intent_fails(self):
        """Test validation fails with empty intent."""
        # Given
        parsed = {
            "intent": "",
            "desired_outcomes": ["Test"],
            "agenda": [],
            "roles": {},
            "rules": [],
            "total_duration_minutes": 30
        }
        
        # When
        errors = self.service.validate_idoarrt(parsed)
        
        # Then
        assert any("intent" in error.lower() for error in errors)

    def test_validate_zero_duration_fails(self):
        """Test validation fails with zero duration."""
        # Given
        parsed = {
            "intent": "Test",
            "desired_outcomes": ["Test"],
            "agenda": [],
            "roles": {},
            "rules": [],
            "total_duration_minutes": 0
        }
        
        # When
        errors = self.service.validate_idoarrt(parsed)
        
        # Then
        assert any("duration" in error.lower() for error in errors)

    def test_validate_agenda_time_exceeds_total_fails(self):
        """Test validation fails when agenda time exceeds total time."""
        # Given
        parsed = {
            "intent": "Test",
            "desired_outcomes": ["Test"],
            "agenda": [
                {"topic": "Intro", "duration_minutes": 25},
                {"topic": "Discussion", "duration_minutes": 10}
            ],
            "roles": {},
            "rules": [],
            "total_duration_minutes": 30
        }
        
        # When
        errors = self.service.validate_idoarrt(parsed)
        
        # Then
        assert any("agenda time" in error.lower() for error in errors)
