from contextlib import asynccontextmanager
from typing import AsyncIterator, TypedDict

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from strawberry.fastapi import GraphQLRouter

from aster.auth.api import login_router, user_router, users_router
from aster.cache import RedisCache
from aster.config import get_settings
from aster.graph import schema
from aster.logging import StructLoggingConfig
from aster.middlewares import (
    CorrelationIDMiddleware,
    LoggingMiddleware,
    TimingMiddleware,
)
from aster.posts.api import posts_router
from aster.routes import AsterRoute


class State(TypedDict):
    cache: RedisCache | None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    cache = (
        RedisCache(str(get_settings().redis_url)) if get_settings().redis_url else None
    )
    yield State(cache=cache)
    if cache:
        await cache.close()


def create_app() -> FastAPI:
    logger = StructLoggingConfig().configure()()
    logger.info("Launching aster")

    app = FastAPI(title="Aster")
    app.router.route_class = AsterRoute
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().cors_origin,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TimingMiddleware)
    app.add_middleware(CorrelationIDMiddleware)
    app.add_middleware(LoggingMiddleware, logger=logger)

    graphql_app = GraphQLRouter(schema)

    async def healthcheck() -> Response:
        return Response("Hello world!")

    app.add_api_route("/health", healthcheck)
    app.include_router(login_router)
    app.include_router(user_router)
    app.include_router(users_router)
    app.include_router(posts_router)
    app.include_router(graphql_app, prefix="/graphql", include_in_schema=False)

    Instrumentator().instrument(app).expose(app, include_in_schema=False)

    return app
