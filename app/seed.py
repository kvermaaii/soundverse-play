import logging

from app.database import SessionLocal
from app.models import SoundClip

logger = logging.getLogger(__name__)

SEED_CLIPS = [
    {
        "title": "Ambient Waves",
        "description": "A calming ambient track with layered synthesizers",
        "genre": "ambient",
        "duration": 337.0,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    },
    {
        "title": "Electronic Pulse",
        "description": "Upbeat electronic track with driving bassline",
        "genre": "electronic",
        "duration": 384.0,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    },
    {
        "title": "Synth Dreams",
        "description": "Melodic electronic composition with retro synths",
        "genre": "electronic",
        "duration": 310.0,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    },
    {
        "title": "Pop Vibes",
        "description": "Catchy pop tune with modern production",
        "genre": "pop",
        "duration": 316.0,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
    },
    {
        "title": "Deep Atmosphere",
        "description": "Deep ambient soundscape for relaxation",
        "genre": "ambient",
        "duration": 326.0,
        "audio_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
    },
    {
        "title": "Quick Sample",
        "description": "Short electronic sample clip for testing",
        "genre": "electronic",
        "duration": 6.0,
        "audio_url": "https://samplelib.com/lib/preview/mp3/sample-6s.mp3",
    },
]


def seed_db_if_empty() -> None:
    db = SessionLocal()
    try:
        count = db.query(SoundClip).count()
        if count == 0:
            logger.info("Database is empty, seeding with %d clips", len(SEED_CLIPS))
            for clip_data in SEED_CLIPS:
                clip = SoundClip(**clip_data)
                db.add(clip)
            db.commit()
            logger.info("Database seeded successfully")
        else:
            logger.info("Database already has %d clips, skipping seed", count)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
