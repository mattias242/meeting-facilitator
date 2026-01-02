"""Audio processing service."""

import subprocess
import tempfile
from collections.abc import Iterator
from pathlib import Path


class AudioChunkData:
    """Data container for an audio chunk."""

    def __init__(self, chunk_number: int, audio_data: bytes, duration_seconds: float):
        self.chunk_number = chunk_number
        self.audio_data = audio_data
        self.duration_seconds = duration_seconds


class AudioService:
    """Service for processing audio files."""

    @staticmethod
    def fix_webm_duration(audio_data: bytes) -> bytes:
        """
        Fix WebM file to include duration metadata.

        MediaRecorder creates WebM files without duration metadata,
        which prevents HTML5 audio elements from playing them correctly.

        Args:
            audio_data: Original WebM audio data

        Returns:
            Fixed WebM audio data with duration metadata

        Raises:
            RuntimeError: If ffmpeg processing fails
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.webm"
            output_path = Path(tmpdir) / "output.webm"

            # Write input file
            input_path.write_bytes(audio_data)

            # Run ffmpeg to remux and add duration
            # -c copy: Don't re-encode, just copy streams
            # -f webm: Force WebM output format
            result = subprocess.run(
                [
                    "ffmpeg",
                    "-y",  # Overwrite output
                    "-i",
                    str(input_path),
                    "-c",
                    "copy",  # Copy codec (no re-encoding)
                    "-f",
                    "webm",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg failed: {result.stderr}")

            # Read and return fixed file
            return output_path.read_bytes()

    @staticmethod
    def split_audio_into_chunks(
        audio_data: bytes, chunk_duration_minutes: int = 2
    ) -> Iterator[AudioChunkData]:
        """
        Split audio file into chunks of specified duration.

        This is useful for testing - upload a full meeting recording
        and split it into chunks as if it was recorded live.

        Args:
            audio_data: Audio file data (any format supported by ffmpeg)
            chunk_duration_minutes: Duration of each chunk in minutes

        Yields:
            AudioChunkData objects for each chunk

        Raises:
            RuntimeError: If ffmpeg processing fails
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            input_path = tmpdir_path / "input.audio"

            # Write input file
            input_path.write_bytes(audio_data)

            # Get total duration
            probe_result = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "default=noprint_wrappers=1:nokey=1",
                    str(input_path),
                ],
                capture_output=True,
                text=True,
            )

            if probe_result.returncode != 0:
                raise RuntimeError(f"ffprobe failed: {probe_result.stderr}")

            try:
                total_duration = float(probe_result.stdout.strip())
            except ValueError as e:
                raise RuntimeError("Could not determine audio duration") from e

            # Calculate chunk parameters
            chunk_duration_seconds = chunk_duration_minutes * 60
            num_chunks = int(total_duration / chunk_duration_seconds) + (
                1 if total_duration % chunk_duration_seconds > 0 else 0
            )

            # Split into chunks
            for chunk_num in range(1, num_chunks + 1):
                start_time = (chunk_num - 1) * chunk_duration_seconds
                output_path = tmpdir_path / f"chunk_{chunk_num}.webm"

                # Extract chunk with ffmpeg
                # -ss: start time
                # -t: duration
                # -c:a opus: encode to opus
                # -b:a 128k: bitrate
                result = subprocess.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-i",
                        str(input_path),
                        "-ss",
                        str(start_time),
                        "-t",
                        str(chunk_duration_seconds),
                        "-c:a",
                        "libopus",
                        "-b:a",
                        "128k",
                        "-f",
                        "webm",
                        str(output_path),
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    raise RuntimeError(f"ffmpeg chunk {chunk_num} failed: {result.stderr}")

                # Get actual chunk duration
                probe_result = subprocess.run(
                    [
                        "ffprobe",
                        "-v",
                        "error",
                        "-show_entries",
                        "format=duration",
                        "-of",
                        "default=noprint_wrappers=1:nokey=1",
                        str(output_path),
                    ],
                    capture_output=True,
                    text=True,
                )

                chunk_duration = float(probe_result.stdout.strip())
                chunk_data = output_path.read_bytes()

                yield AudioChunkData(
                    chunk_number=chunk_num,
                    audio_data=chunk_data,
                    duration_seconds=chunk_duration,
                )
