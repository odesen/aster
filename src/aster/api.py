import fastapi
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from aster.auth.api import login_router, user_router, users_router
from aster.logging import init_logging
from aster.middlewares import (
    CorrelationIDMiddleware,
    LoggingMiddleware,
    TimingMiddleware,
)
from aster.posts.api import posts_router


def create_app() -> fastapi.FastAPI:
    init_logging()

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
