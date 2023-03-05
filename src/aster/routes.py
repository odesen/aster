from typing import Any, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.datastructures import Address, UploadFile
from structlog.contextvars import bind_contextvars


def get_client_addr(client: Address | None) -> str | None:
    if client is None:
        return None
    return f"{client[0]}:{client[1]}"


async def extract_body(request: Request) -> Any:
    if request.method != "GET":
        request_encoding_type = request.headers.get("Content-Type", "")
        if request_encoding_type == "application/json":
            return await request.json()
        form_data = await request.form()
        if request_encoding_type == "application/x-www-form-urlencoded":
            return dict(form_data)
        if form_data:
            return {
                key: repr(value) if isinstance(value, UploadFile) else value
                for key, value in form_data.multi_items()
            }
        return await request.body()
    return None


class AsterRoute(APIRoute):
    def get_route_handler(self) -> Callable:  # type: ignore
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            opt_context = {
                "client": get_client_addr(request.client),
                "body": await extract_body(request),
            }
            bind_contextvars(
                path=request.url.path,
                method=request.method,
                **{k: v for k, v in opt_context.items() if v is not None},
            )
            response = await original_route_handler(request)
            return response

        return custom_route_handler


async def default_exception_handler(request: Request, exc: Exception) -> Response:
    return JSONResponse(status_code=500, content={"message": "error"})
