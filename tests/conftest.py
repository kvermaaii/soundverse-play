import os
from unittest.mock import patch

# Override settings BEFORE any app imports so that module-level objects
# (engine, settings) pick up test values instead of production defaults.
os.environ["API_KEY"] = "test-api-key"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.database import Base, get_db  # noqa: E402
from app.main import create_app  # noqa: E402
from app.models import SoundClip  # noqa: E402

TEST_DATABASE_URL = "sqlite:///./test.db"

engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine_test)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Patch seed_db_if_empty so the lifespan does not insert seed data
    # into the test database -- tests control their own data via fixtures.
    with patch("app.main.seed_db_if_empty"):
        app = create_app()
        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app) as tc:
            yield tc
        app.dependency_overrides.clear()


@pytest.fixture()
def api_headers():
    return {"X-API-Key": "test-api-key"}


@pytest.fixture()
def seed_clips(db_session):
    clips = [
        SoundClip(
            title="Test Ambient",
            description="A calm ambient track",
            genre="ambient",
            duration=30.0,
            audio_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
            play_count=0,
        ),
        SoundClip(
            title="Test Pop",
            description="An upbeat pop track",
            genre="pop",
            duration=25.0,
            audio_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
            play_count=5,
        ),
    ]
    db_session.add_all(clips)
    db_session.commit()
    for clip in clips:
        db_session.refresh(clip)
    return clips
