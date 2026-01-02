"""Fix existing audio chunks in database."""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import DATABASE_URL
from app.models.meeting import AudioChunk
from app.services.audio_service import AudioService

# Create database session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def fix_all_chunks():
    """Fix all audio chunks in database."""
    db = SessionLocal()
    try:
        chunks = db.query(AudioChunk).all()
        print(f"Found {len(chunks)} audio chunks")

        for i, chunk in enumerate(chunks, 1):
            print(f"Processing chunk {i}/{len(chunks)}: {chunk.id} (chunk #{chunk.chunk_number})...")

            try:
                # Fix WebM duration
                fixed_audio = AudioService.fix_webm_duration(chunk.audio_blob)

                # Update in database
                chunk.audio_blob = fixed_audio  # type: ignore[assignment]
                db.commit()

                print(f"  ✓ Fixed (size: {len(chunk.audio_blob)} → {len(fixed_audio)} bytes)")
            except Exception as e:
                print(f"  ✗ Error: {e}")
                db.rollback()

        print("\nDone!")
    finally:
        db.close()


if __name__ == "__main__":
    fix_all_chunks()
