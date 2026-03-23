import logging
from collections.abc import Generator

import httpx
from sqlalchemy.orm import Session

from app.exceptions import ClipNotFoundError, StreamError
from app.models import SoundClip

logger = logging.getLogger(__name__)


def get_all_clips(db: Session) -> list[SoundClip]:
    return db.query(SoundClip).order_by(SoundClip.created_at).all()


def get_clip_by_id(db: Session, clip_id: int) -> SoundClip:
    clip = db.query(SoundClip).filter(SoundClip.id == clip_id).first()
    if clip is None:
        raise ClipNotFoundError(clip_id)
    return clip


def increment_play_count(db: Session, clip_id: int) -> None:
    db.query(SoundClip).filter(SoundClip.id == clip_id).update(
        {SoundClip.play_count: SoundClip.play_count + 1}
    )
    db.commit()


def stream_clip_audio(audio_url: str, chunk_size: int) -> Generator[bytes, None, None]:
    try:
        with httpx.Client(follow_redirects=True) as client, client.stream("GET", audio_url) as response:
            response.raise_for_status()
            yield from response.iter_bytes(chunk_size=chunk_size)
    except httpx.HTTPStatusError as exc:
        logger.error("HTTP error streaming audio from %s: %s", audio_url, exc)
        raise StreamError(
            clip_id=0, reason=f"Upstream returned {exc.response.status_code}"
        ) from exc
    except httpx.RequestError as exc:
        logger.error("Request error streaming audio from %s: %s", audio_url, exc)
        raise StreamError(
            clip_id=0, reason=f"Failed to connect to audio source: {exc}"
        ) from exc


def create_clip(db: Session, clip_data: dict) -> SoundClip:
    clip = SoundClip(**clip_data)
    db.add(clip)
    db.commit()
    db.refresh(clip)
    return clip
