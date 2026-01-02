#!/usr/bin/env python3
"""Test script for transcription service."""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.transcription_service import TranscriptionService


def main() -> None:
    """Test transcription with audio file."""
    audio_file = Path("/Users/mattiaswahlberg/coding/claude-claude/meeting-facilitator/test/kaffemaskin-meeting.mp3")

    if not audio_file.exists():
        print(f"Error: Audio file not found: {audio_file}")
        sys.exit(1)

    print(f"Reading audio file: {audio_file}")
    audio_data = audio_file.read_bytes()
    print(f"Audio file size: {len(audio_data):,} bytes")

    print("\nInitializing transcription service...")
    service = TranscriptionService(model_size="base", device="cpu", compute_type="int8")

    print("Starting transcription...")
    try:
        transcription = service.transcribe_audio(audio_data, language="sv")

        print("\n" + "="*80)
        print("TRANSCRIPTION RESULT:")
        print("="*80)
        print(transcription)
        print("="*80)
        print(f"\nTranscription length: {len(transcription)} characters")

    except Exception as e:
        print(f"\nError during transcription: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
