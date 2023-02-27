import logging
from typing import Any, cast
from uuid import uuid4

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

from .context import correlation_id

logger = logging.getLogger("aster")


class LoggingMiddleware:
    def __init__(self, app: ASGI3Application):
        self.app = app

    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        send = self.create_send_wrapper(scope, send)
        await self.app(scope, receive, send)

    async def extract_request_data(
        self, scope: HTTPScope, receive: ASGIReceiveCallable
    ) -> dict[str, Any]:
        request = Request(
            cast(types.Scope, scope), receive=cast(types.Receive, receive)
        )
        return {
            "path_params": request.path_params,
            "method": request.method,
            "client": request.client,
        }

    async def extract_response_data(
        self, message: HTTPResponseStartEvent
    ) -> dict[str, Any]:
        return {"status": message["status"]}

    async def extract_response_body_data(
        self, message: HTTPResponseBodyEvent
    ) -> dict[str, Any]:
        return {"body": message["body"]}

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
        correlation_id.set(uuid4().hex)
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
