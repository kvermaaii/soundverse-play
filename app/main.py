import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text
from starlette_exporter import PrometheusMiddleware, handle_metrics

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.exceptions import (
    ClipNotFoundError,
    StreamError,
    clip_not_found_handler,
    stream_error_handler,
)
from app.routers.play import router as play_router
from app.seed import seed_db_if_empty

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Seeding database...")
    seed_db_if_empty()
    logger.info("Application startup complete")
    yield
    logger.info("Disposing database engine...")
    engine.dispose()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    application.add_middleware(
        PrometheusMiddleware,
        app_name="soundverse",
        group_paths=True,
        filter_unhandled_paths=True,
    )
    application.add_route("/metrics", handle_metrics)

    application.add_exception_handler(ClipNotFoundError, clip_not_found_handler)
    application.add_exception_handler(StreamError, stream_error_handler)

    application.include_router(play_router)

    @application.get("/health")
    def health_check() -> dict:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            return {"status": "healthy", "database": "connected"}
        except Exception as exc:
            logger.error("Health check failed: %s", exc)
            return {"status": "unhealthy", "database": "disconnected"}
        finally:
            db.close()

    return application


app = create_app()
