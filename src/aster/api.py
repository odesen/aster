from fastapi import FastAPI, Response
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from aster.auth.api import login_router, user_router, users_router
from aster.logging import StructLoggingConfig
from aster.middlewares import (
    CorrelationIDMiddleware,
    LoggingMiddleware,
    TimingMiddleware,
)
from aster.posts.api import posts_router
from aster.routes import default_exception_handler


def create_app() -> FastAPI:
    logger = StructLoggingConfig().configure()()
    logger.info("Launching aster")

    app = FastAPI()
    app.add_middleware(TimingMiddleware)
    app.add_middleware(CorrelationIDMiddleware)
    app.add_middleware(LoggingMiddleware, logger=logger)
    app.add_exception_handler(Exception, default_exception_handler)

    async def healthcheck() -> Response:
        return Response("Hello world!")

    app.add_api_route("/health", healthcheck)
    app.include_router(login_router)
    app.include_router(user_router)
    app.include_router(users_router)
    app.include_router(posts_router)

    FastAPIInstrumentor.instrument_app(app)
    return app
