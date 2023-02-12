import fastapi
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from aster.auth.api import user_router, users_router
from aster.posts.api import posts_router


def create_app() -> fastapi.FastAPI:
    app = fastapi.FastAPI()

    async def healthcheck() -> fastapi.Response:
        return fastapi.Response("Hello world!")

    app.add_api_route("/health", healthcheck)

    app.include_router(user_router)
    app.include_router(users_router)
    app.include_router(posts_router)

    FastAPIInstrumentor.instrument_app(app)
    return app
