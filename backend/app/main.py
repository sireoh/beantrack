"""Application factory.

Run with:  uvicorn app.main:create_app --factory
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routers import auth, movielist, search, tvlist
from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.db.session import build_engine, build_sessionmaker

USER_AGENT = "BeanTrack/0.1"


async def _app_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


def create_app(
    settings: Settings | None = None, http_client: httpx.Client | None = None
) -> FastAPI:
    """Build the app. Tests pass their own settings and an httpx client with a mock transport."""
    settings = settings or get_settings()
    engine = build_engine(settings.database_url)
    http = http_client or httpx.Client(
        timeout=10.0, follow_redirects=True, headers={"User-Agent": USER_AGENT}
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        yield
        http.close()
        engine.dispose()

    app = FastAPI(title="BeanTrack API", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = engine
    app.state.sessionmaker = build_sessionmaker(engine)
    app.state.http_client = http
    app.add_exception_handler(AppError, _app_error_handler)

    api = APIRouter()

    @api.get("/health", tags=["meta"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    api.include_router(auth.router)
    api.include_router(tvlist.router)
    api.include_router(movielist.router)
    api.include_router(search.router)
    app.include_router(api, prefix="/api")
    return app
