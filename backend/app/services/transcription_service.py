"""Transcription service using faster_whisper."""

import tempfile
from pathlib import Path
from typing import Any


class TranscriptionService:
    """Service for transcribing audio using faster_whisper."""

    def __init__(
        self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"
    ) -> None:
        """
        Initialize transcription service.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: Device to run on (cpu, cuda, auto)
            compute_type: Compute type (int8, float16, float32)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        # Lazy load model - will be loaded on first use
        self._model: Any = None

    def _load_model(self) -> None:
        """Load model on first use."""
        if self._model is None:
            from faster_whisper import WhisperModel  # type: ignore[import-not-found]

            print(f"Loading faster_whisper model: {self.model_size} on {self.device}...")
            self._model = WhisperModel(
                self.model_size, device=self.device, compute_type=self.compute_type
            )
            print("Model loaded successfully")

    def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "sv",
        prompt: str | None = None,
        beam_size: int = 5,
    ) -> str:
        """
        Transcribe audio using faster_whisper.

        Args:
            audio_data: Audio file data (WebM, MP3, WAV, etc.)
            language: Language code (default: "sv" for Swedish)
            prompt: Optional prompt to guide transcription
            beam_size: Beam size for decoding (default: 5)

        Returns:
            Transcribed text

        Raises:
            RuntimeError: If transcription fails
        """
        self._load_model()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_path = tmpdir_path / "input.audio"

            # Write input file
            input_path.write_bytes(audio_data)

            try:
                # Transcribe directly (faster_whisper handles format conversion)
                segments, info = self._model.transcribe(
                    str(input_path),
                    language=language,
                    beam_size=beam_size,
                    initial_prompt=prompt,
                )

                # Concatenate all segments
                full_text = " ".join(segment.text.strip() for segment in segments)

                return full_text.strip()

            except Exception as e:
                raise RuntimeError(f"Transcription failed: {str(e)}") from e

    def transcribe_audio_with_context(
        self,
        audio_data: bytes,
        meeting_context: str | None = None,
        language: str = "sv",
    ) -> str:
        """
        Transcribe audio with meeting context to improve accuracy.

        Args:
            audio_data: Audio file data
            meeting_context: Context about the meeting (intent, topics, etc.)
            language: Language code

        Returns:
            Transcribed text
        """
        # Build prompt with context
        prompt = None
        if meeting_context:
            prompt = f"Detta är en möteskonversation. Kontext: {meeting_context[:200]}"

        return self.transcribe_audio(audio_data, language=language, prompt=prompt)
