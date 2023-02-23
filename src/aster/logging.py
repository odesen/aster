import logging
import uuid

from .context import current_context

DEFAULT_LOGGING_CONFIG: dict = {  # type: ignore
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "context": {
            "()": "aster.logging.ContextFilter",
        }
    },
    "formatters": {
        "access": {
            "format": "{levelname} {asctime} {client_addr} {request_line} {status_code} {process_time}",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "style": "{",
        },
    },
    "handlers": {
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "filters": ["context"],
        },
    },
    "loggers": {
        "aster.access": {"level": "INFO", "handlers": ["access"], "propagate": False},
    },
}


class ContextFilter(logging.Filter):
    def __init__(self) -> None:
        super().__init__()

    def filter(self, record: logging.LogRecord) -> bool:
        context = current_context.get()
        record.request_id = context.get("request_id", uuid.UUID(int=0).hex)
        record.client_addr = context.get("client_addr", "")
        record.request_line = context.get("r")
        record.status_code = context.get("status_code")
        record.process_time = context.get("T", 0)
        return True
