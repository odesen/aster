import logging.config

import fastapi
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from aster.auth.api import login_router, user_router, users_router
from aster.logging import DEFAULT_LOGGING_CONFIG
from aster.middlewares import AsterMiddleware
from aster.posts.api import posts_router


def create_app() -> fastapi.FastAPI:
    logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)

    app = fastapi.FastAPI()
    app.add_middleware(AsterMiddleware)

    async def healthcheck() -> fastapi.Response:
        return fastapi.Response("Hello world!")

    app.add_api_route("/health", healthcheck)
    app.include_router(login_router)
    app.include_router(user_router)
    app.include_router(users_router)
    app.include_router(posts_router)

    FastAPIInstrumentor.instrument_app(app)
    return app
