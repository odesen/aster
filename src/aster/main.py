import fastapi
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from aster.auth.api import user_router, users_router
from aster.posts.api import posts_router


def create_app() -> fastapi.FastAPI:
    from aster.database import engine
    from aster.models import Base

    app = fastapi.FastAPI()

    async def healthcheck() -> fastapi.Response:
        return fastapi.Response("Hello world!")

    app.add_api_route("/health", healthcheck)

    async def startup() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    app.add_event_handler("startup", startup)

    app.include_router(user_router)
    app.include_router(users_router)
    app.include_router(posts_router)

    FastAPIInstrumentor.instrument_app(app)
    return app
