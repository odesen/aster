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
    HTTPScope,
    Scope,
)
from fastapi import Request
from starlette import datastructures, types
from structlog.contextvars import bind_contextvars, clear_contextvars

from .context import correlation_id

logger = structlog.get_logger()


def get_client_addr(client: datastructures.Address | None) -> str:
    if client is None:
        return "unknown:unknown"
    return f"{client[0]}:{client[1]}"


class LoggingMiddleware:
    def __init__(self, app: ASGI3Application):
        self.app = app

    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        await self.extract_request_data(scope, receive)
        send = self.create_send_wrapper(scope, send)
        log = logger.bind()
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            await log.exception("Exception during request: %s" % type(exc))
            raise exc
        else:
            await log.info("HTTP Request")
        clear_contextvars()

    async def extract_request_data(
        self, scope: HTTPScope, receive: ASGIReceiveCallable
    ) -> None:
        request = Request(
            cast(types.Scope, scope), receive=cast(types.Receive, receive)
        )
        bind_contextvars(
            path=scope["path"],
            method=request.method,
            client=get_client_addr(request.client),
            body=await request.body(),
        )

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
        send = self.create_send_wrapper(scope, send)
        await self.app(scope, receive, send)

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
        except Exception as exc:
            raise exc
        finally:
            bind_contextvars(process_time=time.time() - start)
