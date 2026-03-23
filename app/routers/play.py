import time

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.metrics import STREAM_COUNTER, STREAM_LATENCY
from app.schemas import (
    ClipListResponse,
    SoundClipCreate,
    SoundClipResponse,
    SoundClipStats,
)
from app.services import clip_service

router = APIRouter(prefix="/play", tags=["play"])


def verify_api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return x_api_key


@router.get("", response_model=ClipListResponse)
def list_clips(
    db: Session = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> ClipListResponse:
    clips = clip_service.get_all_clips(db)
    return ClipListResponse(
        clips=[SoundClipResponse.model_validate(c) for c in clips],
        count=len(clips),
    )


@router.get("/{clip_id}/stream")
def stream_clip(
    clip_id: int,
    db: Session = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> StreamingResponse:
    clip = clip_service.get_clip_by_id(db, clip_id)
    clip_service.increment_play_count(db, clip_id)

    STREAM_COUNTER.labels(clip_id=str(clip_id)).inc()
    start_time = time.perf_counter()

    def audio_generator():
        try:
            yield from clip_service.stream_clip_audio(
                clip.audio_url, settings.STREAM_CHUNK_SIZE
            )
        finally:
            duration = time.perf_counter() - start_time
            STREAM_LATENCY.labels(clip_id=str(clip_id)).observe(duration)

    return StreamingResponse(
        content=audio_generator(),
        media_type="audio/mpeg",
    )


@router.get("/{clip_id}/stats", response_model=SoundClipStats)
def get_clip_stats(
    clip_id: int,
    db: Session = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> SoundClipStats:
    clip = clip_service.get_clip_by_id(db, clip_id)
    return SoundClipStats.model_validate(clip)


@router.post("", response_model=SoundClipResponse, status_code=status.HTTP_201_CREATED)
def create_clip(
    clip_data: SoundClipCreate,
    db: Session = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
) -> SoundClipResponse:
    clip = clip_service.create_clip(db, clip_data.model_dump())
    return SoundClipResponse.model_validate(clip)
