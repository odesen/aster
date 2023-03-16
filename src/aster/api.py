from contextlib import asynccontextmanager
from typing import AsyncIterator, TypedDict

from fastapi import FastAPI, Response

# from opentelemetry import trace
# from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from strawberry.fastapi import GraphQLRouter

# from opentelemetry.sdk.resources import SERVICE_NAME, Resource
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor
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
    app.include_router(graphql_app, prefix="/graphql")

    FastAPIInstrumentor.instrument_app(app)
    # resource = Resource(attributes={SERVICE_NAME: "aster"})
    # jaeger_exporter = JaegerExporter(agent_host_name="localhost", agent_port=6831)
    # provider = TracerProvider(resource=resource)
    # processor = BatchSpanProcessor(jaeger_exporter)
    # provider.add_span_processor(processor)
    # trace.set_tracer_provider(provider)
    return app
