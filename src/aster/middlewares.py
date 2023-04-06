import time
from typing import cast
from uuid import uuid4

import structlog
from asgiref.typing import (
    ASGI3Application,
    ASGIReceiveCallable,
    ASGISendCallable,
    ASGISendEvent,
    HTTPResponseBodyEvent,
    HTTPResponseStartEvent,
    Scope,
)
from starlette import datastructures, types
from structlog.contextvars import bind_contextvars, clear_contextvars

from .context import correlation_id

logger = structlog.get_logger()


class LoggingMiddleware:
    def __init__(
        self, app: ASGI3Application, logger: structlog.types.FilteringBoundLogger
    ):
        self.app = app
        self.logger = logger

    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        clear_contextvars()
        send = self.create_send_wrapper(scope, send)
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            await self.logger.aexception("Exception during request: %s" % type(exc))
            raise exc
        else:
            await self.logger.ainfo("HTTP Request")

    async def extract_response_data(self, message: HTTPResponseStartEvent) -> None:
        bind_contextvars(
            status=message["status"],
        )

    async def extract_response_body_data(self, message: HTTPResponseBodyEvent) -> None:
        # {"body": message["body"]}
        ...

    def create_send_wrapper(
        self, scope: Scope, send: ASGISendCallable
    ) -> ASGISendCallable:
        async def send_wrapper(message: ASGISendEvent) -> None:
            if message["type"] == "http.response.start":
                await self.extract_response_data(message)
            elif message["type"] == "http.response.body":
                await self.extract_response_body_data(message)
            await send(message)

        return send_wrapper


class CorrelationIDMiddleware:
    def __init__(self, app: ASGI3Application, header_name: str = "X-Request-ID"):
        self.app = app
        self.header_name = header_name

    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        correlation_id.set(id_value := uuid4().hex)
        bind_contextvars(request_id=id_value)
        sender = self.create_send_wrapper(scope, send)
        await self.app(scope, receive, sender)

    def create_send_wrapper(
        self, scope: Scope, send: ASGISendCallable
    ) -> ASGISendCallable:
        async def send_wrapper(message: ASGISendEvent) -> None:
            if message["type"] == "http.response.start" and (
                id_value := correlation_id.get()
            ):
                headers = datastructures.MutableHeaders(
                    scope=cast(types.Message, message)
                )
                headers.append(self.header_name, id_value)
            await send(message)

        return send_wrapper


class TimingMiddleware:
    def __init__(self, app: ASGI3Application):
        self.app = app

    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        try:
            start = time.time()
            await self.app(scope, receive, send)
        finally:
            bind_contextvars(process_time=time.time() - start)
