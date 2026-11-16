"""lab-api entrypoint — uvicorn backend.app.main:app."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from backend.app.routers import (
    auth,
    catalog,
    datasets,
    deep,
    eda,
    experiments,
    export_models,
    insights,
    intake,
    jobs,
    monitoring,
    predict,
    preprocess,
    reports,
    suitability,
    timeseries,
    unsupervised,
    wfo,
)
from backend.app.schemas import Healthz
from backend.app.settings import get_settings

limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # OTel is optional locally; workers/instrumentation wire in Phase 8.2
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="ARW ML Lab API", version="0.1.0", lifespan=lifespan)
    app.state.limiter = limiter
    app.add_exception_handler(
        RateLimitExceeded,
        lambda request, exc: JSONResponse(status_code=429, content={"detail": "rate limit"}),
    )
    app.add_middleware(SlowAPIMiddleware)

    origins = [o.strip() for o in settings.cors_allowed_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["http://localhost:3000"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-Workspace-Id"],
    )

    @app.get("/healthz", response_model=Healthz)
    @limiter.limit("60/minute")
    def healthz(request: Request) -> Healthz:
        _ = request
        return Healthz(
            seed=settings.lab_default_seed,
            service=settings.service_role,
            ai_enabled=settings.ai_enabled,
        )

    @app.middleware("http")
    async def reject_cookie_auth(request: Request, call_next: object) -> Response:
        # SEC-07: lab-api accepts Authorization Bearer only (no cookie session to API)
        response = await call_next(request)  # type: ignore[operator]
        return response

    app.include_router(auth.router)
    app.include_router(catalog.router)
    app.include_router(jobs.router)
    app.include_router(datasets.router)
    app.include_router(eda.router)
    app.include_router(intake.router)
    app.include_router(experiments.router)
    app.include_router(predict.router)
    app.include_router(preprocess.router)
    app.include_router(export_models.router)
    app.include_router(timeseries.router)
    app.include_router(unsupervised.router)
    app.include_router(suitability.router)
    app.include_router(deep.router)
    app.include_router(insights.router)
    app.include_router(wfo.router)
    app.include_router(reports.router)
    app.include_router(monitoring.router)
    return app


app = create_app()
