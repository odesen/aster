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

logger = logging.getLogger("aster.access")


class AsterMiddleware:
    def __init__(self, app: ASGI3Application):
        self.app = app

    async def __call__(
        self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        context = AsterCanonicalLogAtoms()
        current_context.set(context)
        context.update(request_id=uuid.uuid4().hex)
        context.update_request(scope)
        start_time = time.time()

        async def inner_send(message: ASGISendEvent) -> None:
            if message["type"] == "http.response.start":
                context.update_response(message)
            await send(message)

        try:
            await self.app(scope, receive, inner_send)
        except Exception:
            raise
        finally:
            context.update_process_time(time.time() - start_time)
            logger.info("request")
