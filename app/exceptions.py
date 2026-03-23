from fastapi import Request
from fastapi.responses import JSONResponse


class ClipNotFoundError(Exception):
    def __init__(self, clip_id: int) -> None:
        self.clip_id = clip_id
        self.message = f"Sound clip with id {clip_id} not found"
        super().__init__(self.message)


class StreamError(Exception):
    def __init__(self, clip_id: int, reason: str) -> None:
        self.clip_id = clip_id
        self.reason = reason
        self.message = f"Stream error for clip {clip_id}: {reason}"
        super().__init__(self.message)


def clip_not_found_handler(request: Request, exc: ClipNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message},
    )


def stream_error_handler(request: Request, exc: StreamError) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content={"detail": exc.message},
    )
