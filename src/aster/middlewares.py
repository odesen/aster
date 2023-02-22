import logging
import time
import uuid

from asgiref.typing import (
    ASGI3Application,
    ASGIReceiveCallable,
    ASGISendCallable,
    ASGISendEvent,
    Scope,
)

from aster.context import AsterCanonicalLogAtoms, current_context

logger = logging.getLogger("aster")


class AsterMiddleware:
    def __init__(self, app: ASGI3Application):
        self.app = app

    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        current_context.set(AsterCanonicalLogAtoms())
        request_id: str = uuid.uuid4().hex
        current_context.get().update(request_id=request_id)
        start_time = time.time()

        async def inner_send(message: ASGISendEvent) -> None:
            if message["type"] == "http.response.start":
                current_context.get().update_response(message)
            await send(message)

        try:
            await self.app(scope, receive, inner_send)
        except Exception:
            raise
        finally:
            current_context.get().update_request(scope)
            current_context.get().update_process_time(time.time() - start_time)
            logger.info(
                "%(t)s - %(client_addr)s - %(request_line)s", current_context.get()
            )
