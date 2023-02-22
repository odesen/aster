import http
import time
from contextvars import ContextVar
from urllib.parse import quote

from asgiref.typing import HTTPResponseStartEvent, HTTPScope


def get_client_addr(scope: HTTPScope) -> str:
    if scope["client"] is None:
        return "unknown:unknown"
    return f"{scope['client'][0]:{scope['client'][1]}}"


def get_path_with_query_string(scope: HTTPScope) -> str:
    path_with_query_string = quote(scope.get("root_path", "") + scope["path"])
    if scope["query_string"]:  # pragma: no cover
        return f"{path_with_query_string}?{scope['query_string'].decode('ascii')}"
    return path_with_query_string


class AsterCanonicalLogAtoms(dict):  # type: ignore
    def __init__(self) -> None:
        ...

    def update_request(self, scope: HTTPScope) -> None:
        for name, value in scope["headers"]:
            self[f"{{{name.decode('latin1').lower()}}}i"] = value.decode("latin1")

        protocol = f"HTTP/{scope['http_version']}"

        path = scope["root_path"] + scope["path"]
        full_path = get_path_with_query_string(scope)
        request_line = f"{scope['method']} {path} {protocol}"
        full_request_line = f"{scope['method']} {full_path} {protocol}"

        client_addr = get_client_addr(scope)
        self.update(
            {
                "h": client_addr,
                "client_addr": client_addr,
                "l": "-",
                "u": "-",  # Not available on ASGI.
                "t": time.strftime("[%d/%b/%Y:%H:%M:%S %z]"),
                "r": request_line,
                "request_line": full_request_line,
                "R": full_request_line,
                "m": scope["method"],
                "U": scope["path"],
                "q": scope["query_string"].decode(),
                "H": protocol,
                "B": self["{Content-Length}o"],
                "b": self.get("{Content-Length}o", "-"),
                "f": self["{Referer}i"],
                "a": self["{User-Agent}i"],
            }
        )

    def update_response(self, send: HTTPResponseStartEvent) -> None:
        for name, value in send.get("headers", []):
            self[f"{{{name.decode('latin1').lower()}}}o"] = value.decode("latin1")

        status = send["status"]
        try:
            status_phrase = http.HTTPStatus(status).phrase
        except ValueError:
            status_phrase = "-"

        self.update(
            {
                "s": status,
                "status_code": f"{status} {status_phrase}",
                "st": status_phrase,
                "B": self["{Content-Length}o"],
                "b": self.get("{Content-Length}o", "-"),
                "f": self["{Referer}i"],
                "a": self["{User-Agent}i"],
            }
        )

    def update_process_time(self, process_time: float) -> None:
        self.update(
            {
                "T": int(process_time),
                "M": int(process_time * 1_000),
                "D": int(process_time * 1_000_000),
            }
        )

    def __getitem__(self, key: str) -> str:
        try:
            if key.startswith("{"):
                return super().__getitem__(key.lower())
            else:
                return super().__getitem__(key)
        except KeyError:
            return "-"


current_context: ContextVar[AsterCanonicalLogAtoms] = ContextVar(
    "aster_context", default=AsterCanonicalLogAtoms()
)
