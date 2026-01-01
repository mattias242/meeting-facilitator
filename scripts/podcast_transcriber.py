#!/usr/bin/env python3
"""
Podcast Transcriber
Transcribes downloaded podcast episodes using Whisper API or local Whisper model.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import subprocess


class PodcastTranscriber:
    def __init__(
        self,
        input_dir: str = "podcast_downloads",
        output_dir: str = "podcast_transcripts",
        api_key: Optional[str] = None,
        use_local: bool = False
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.use_local = use_local

    def check_whisper_installed(self) -> bool:
        """Check if local Whisper is installed."""
        try:
            import whisper
            return True
        except ImportError:
            return False

    def install_whisper(self):
        """Install OpenAI Whisper locally."""
        print("Installing openai-whisper...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "openai-whisper"],
            check=True
        )
        print("Whisper installed successfully!")

    def transcribe_with_api(self, audio_file: Path) -> Dict:
        """Transcribe using OpenAI Whisper API."""
        try:
            from openai import OpenAI
        except ImportError:
            print("Installing openai package...")
            subprocess.run([sys.executable, "-m", "pip", "install", "openai"], check=True)
            from openai import OpenAI

        if not self.api_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or use --local flag for local transcription."
            )

        client = OpenAI(api_key=self.api_key)

        print(f"Transcribing {audio_file.name} with Whisper API...")

        with open(audio_file, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                language="sv",  # Swedish
                response_format="verbose_json"
            )

        return {
            'text': transcript.text,
            'language': transcript.language,
            'duration': transcript.duration,
            'segments': transcript.segments if hasattr(transcript, 'segments') else []
        }

    def transcribe_with_local(self, audio_file: Path, model_size: str = "base") -> Dict:
        """Transcribe using local Whisper model."""
        if not self.check_whisper_installed():
            print("Local Whisper not found. Installing...")
            self.install_whisper()

        import whisper

        print(f"Loading Whisper model ({model_size})...")
        model = whisper.load_model(model_size)

        print(f"Transcribing {audio_file.name} locally...")
        result = model.transcribe(
            str(audio_file),
            language="sv",
            verbose=False
        )

        return {
            'text': result['text'],
            'language': result['language'],
            'segments': result.get('segments', [])
        }

    def transcribe_file(self, audio_file: Path, model_size: str = "base") -> Optional[Dict]:
        """Transcribe a single audio file."""
        try:
            if self.use_local:
                result = self.transcribe_with_local(audio_file, model_size)
            else:
                result = self.transcribe_with_api(audio_file)

            # Save transcript
            output_file = self.output_dir / f"{audio_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            # Also save plain text version
            text_file = self.output_dir / f"{audio_file.stem}.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(result['text'])

            print(f"✓ Saved transcript to: {output_file}")
            print(f"✓ Saved text to: {text_file}")

            return result

        except Exception as e:
            print(f"✗ Error transcribing {audio_file.name}: {e}")
            return None

    def transcribe_all(self, model_size: str = "base") -> List[Dict]:
        """Transcribe all audio files in input directory."""
        audio_files = list(self.input_dir.glob("*.mp3"))
        audio_files.extend(self.input_dir.glob("*.wav"))
        audio_files.extend(self.input_dir.glob("*.m4a"))

        if not audio_files:
            print(f"No audio files found in {self.input_dir}")
            return []

        print(f"Found {len(audio_files)} audio files")
        print(f"Using {'local Whisper' if self.use_local else 'Whisper API'}")

        results = []
        for i, audio_file in enumerate(audio_files, 1):
            print(f"\n[{i}/{len(audio_files)}] Processing: {audio_file.name}")
            result = self.transcribe_file(audio_file, model_size)
            if result:
                results.append({
                    'filename': audio_file.name,
                    'transcript_file': str(self.output_dir / f"{audio_file.stem}.json"),
                    'text_file': str(self.output_dir / f"{audio_file.stem}.txt"),
                    'text_length': len(result['text']),
                    'language': result.get('language', 'unknown')
                })

        # Save metadata
        metadata_file = self.output_dir / "transcripts_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_transcripts': len(results),
                'transcripts': results,
                'method': 'local' if self.use_local else 'api'
            }, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Metadata saved to: {metadata_file}")
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe podcast episodes using Whisper"
    )
    parser.add_argument(
        "-i", "--input",
        default="podcast_downloads",
        help="Input directory with audio files (default: podcast_downloads)"
    )
    parser.add_argument(
        "-o", "--output",
        default="podcast_transcripts",
        help="Output directory for transcripts (default: podcast_transcripts)"
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use local Whisper model instead of API"
    )
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size for local transcription (default: base)"
    )
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )

    args = parser.parse_args()

    transcriber = PodcastTranscriber(
        input_dir=args.input,
        output_dir=args.output,
        api_key=args.api_key,
        use_local=args.local
    )

    results = transcriber.transcribe_all(model_size=args.model)

    if results:
        print(f"\n{'='*60}")
        print(f"✓ Transcribed {len(results)} episodes")
        print(f"✓ Transcripts saved to: {transcriber.output_dir}")
        print(f"{'='*60}")
        print("\nNext step:")
        print("python scripts/podcast_summarizer.py")
    else:
        print("\n✗ No transcriptions completed")
        sys.exit(1)


if __name__ == "__main__":
    main()
