import logging
import sys

import orjson
import structlog
from structlog.dev import set_exc_info

from .config import get_settings


def init_logging() -> None:
    shared_processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        set_exc_info,
        # structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    if sys.stderr.isatty():
        # processors = shared_processors + [structlog.dev.ConsoleRenderer()]
        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processor=structlog.dev.ConsoleRenderer(
                exception_formatter=structlog.dev.plain_traceback
            ),
        )
    else:
        shared_processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(serializer=orjson.dumps),
        ]
        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processor=structlog.processors.JSONRenderer(serializer=orjson.dumps),
        )
    processors: list[structlog.typing.Processor] = shared_processors + [
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(
        cache_logger_on_first_use=True,
        wrapper_class=structlog.stdlib.AsyncBoundLogger,
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers.clear()
    uvicorn_logger.propagate = True

    uvicorn_error_logger = logging.getLogger("uvicorn.error")
    uvicorn_error_logger.handlers.clear()
    uvicorn_error_logger.propagate = False

    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.handlers.clear()
    uvicorn_access_logger.propagate = False

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(get_settings().logging_level)
    stdout_handler.addFilter(_MaxLevelFilter(logging.WARNING))
    stdout_handler.setFormatter(formatter)
    # handler for high level logs that should be sent to STDERR
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(get_settings().logging_level)
    root_logger.addHandler(stdout_handler)
    root_logger.addHandler(stderr_handler)


class _MaxLevelFilter(logging.Filter):
    def __init__(self, highest_log_level: int) -> None:
        self._highest_log_level = highest_log_level

    def filter(self, log_record: logging.LogRecord) -> bool:
        return log_record.levelno <= self._highest_log_level
