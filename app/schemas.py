from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SoundClipBase(BaseModel):
    title: str
    description: str
    genre: str
    duration: float
    audio_url: str


class SoundClipCreate(SoundClipBase):
    pass


class SoundClipListItem(SoundClipBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class SoundClipResponse(SoundClipBase):
    id: int
    play_count: int
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class SoundClipStats(BaseModel):
    id: int
    title: str
    description: str
    genre: str
    duration: float
    audio_url: str
    play_count: int
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ClipListResponse(BaseModel):
    clips: list[SoundClipListItem]
    count: int


class ErrorResponse(BaseModel):
    detail: str
