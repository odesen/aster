import logging

import fastapi
import orjson
import structlog
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from aster.auth.api import login_router, user_router, users_router
from aster.middlewares import (
    CorrelationIDMiddleware,
    LoggingMiddleware,
    TimingMiddleware,
)
from aster.posts.api import posts_router


def create_app() -> fastapi.FastAPI:
    structlog.configure(
        cache_logger_on_first_use=True,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(serializer=orjson.dumps),
        ],
        logger_factory=structlog.BytesLoggerFactory(),
    )

    app = fastapi.FastAPI()
    app.add_middleware(TimingMiddleware)
    app.add_middleware(CorrelationIDMiddleware)
    app.add_middleware(LoggingMiddleware)

    async def healthcheck() -> fastapi.Response:
        return fastapi.Response("Hello world!")

    app.add_api_route("/health", healthcheck)
    app.include_router(login_router)
    app.include_router(user_router)
    app.include_router(users_router)
    app.include_router(posts_router)

    FastAPIInstrumentor.instrument_app(app)
    return app
