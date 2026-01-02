"""Test Claude service with mocking."""

import pytest
from unittest.mock import Mock, patch
from app.services.claude_service import ClaudeService


class TestClaudeService:
    """Test suite for Claude AI service."""

    def setup_method(self):
        """Set up test instance with mocked API key."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            self.service = ClaudeService()

    @patch('app.services.claude_service.Anthropic')
    def test_init_with_api_key_success(self, mock_anthropic):
        """Test successful initialization with API key."""
        # Given
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        
        # When
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            service = ClaudeService()
        
        # Then
        mock_anthropic.assert_called_once_with(api_key='test-key')
        assert service.model == "claude-sonnet-4-20250514"

    def test_init_without_api_key_raises_error(self):
        """Test initialization fails without API key."""
        # Given
        with patch.dict('os.environ', {}, clear=True):
            # When/Then
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                ClaudeService()

    @patch('app.services.claude_service.Anthropic')
    def test_analyze_transcription_success(self, mock_anthropic):
        """Test successful transcription analysis."""
        # Given
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_message = Mock()
        mock_client.messages.create.return_value = mock_message
        mock_message.content = [Mock(text='{"triggers": [{"type": "goal_deviation", "confidence": 0.8, "reason": "Test"}]}')]
        
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            service = ClaudeService()
        
        transcription = "Test transcription"
        meeting_context = {"intent": "Test", "desired_outcomes": ["Test goal"]}
        history = ["Previous chunk"]
        
        # When
        result = service.analyze_transcription_for_triggers(
            transcription, meeting_context, history
        )
        
        # Then
        assert "triggers" in result
        assert len(result["triggers"]) == 1
        assert result["triggers"][0]["type"] == "goal_deviation"
        assert result["triggers"][0]["confidence"] == 0.8

    @patch('app.services.claude_service.Anthropic')
    def test_analyze_transcription_api_error_returns_empty(self, mock_anthropic):
        """Test API error returns empty triggers."""
        # Given
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")
        
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            service = ClaudeService()
        
        # When
        result = service.analyze_transcription_for_triggers(
            "Test", {"intent": "Test"}, []
        )
        
        # Then
        assert result["triggers"] == []
        assert "error" in result

    @patch('app.services.claude_service.Anthropic')
    def test_generate_facilitation_question_success(self, mock_anthropic):
        """Test successful question generation."""
        # Given
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_message = Mock()
        mock_client.messages.create.return_value = mock_message
        mock_message.content = [Mock(text="Hur relaterar detta till vårt mål?")]
        
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            service = ClaudeService()
        
        # When
        result = service.generate_facilitation_question(
            "goal_deviation", 
            {"reason": "Discussion deviated"}, 
            "Test transcription"
        )
        
        # Then
        assert result == "Hur relaterar detta till vårt mål?"

    @patch('app.services.claude_service.Anthropic')
    def test_generate_facilitation_question_api_error_returns_fallback(self, mock_anthropic):
        """Test API error returns fallback message."""
        # Given
        mock_client = Mock()
        mock_anthropic.return_value = mock_client
        mock_client.messages.create.side_effect = Exception("API Error")
        
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            service = ClaudeService()
        
        # When
        result = service.generate_facilitation_question(
            "goal_deviation", {}, "Test"
        )
        
        # Then
        assert "Fel vid generering av fråga" in result

    def test_parse_trigger_response_valid_json(self):
        """Test parsing valid JSON response."""
        # Given
        response = '{"triggers": [{"type": "test", "confidence": 0.5}]}'
        
        # When
        result = self.service._parse_trigger_response(response)
        
        # Then
        assert result["triggers"][0]["type"] == "test"

    def test_parse_trigger_response_with_extra_text(self):
        """Test parsing JSON with extra text."""
        # Given
        response = 'Some text {"triggers": [{"type": "test"}]} more text'
        
        # When
        result = self.service._parse_trigger_response(response)
        
        # Then
        assert result["triggers"][0]["type"] == "test"

    def test_parse_trigger_response_invalid_json(self):
        """Test parsing invalid JSON returns error."""
        # Given
        response = 'invalid json'
        
        # When
        result = self.service._parse_trigger_response(response)
        
        # Then
        assert result["triggers"] == []
        assert "error" in result
