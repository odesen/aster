import logging
import sys

import orjson
import structlog


def init_logging() -> None:
    shared_processors: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]
    processors: list[structlog.typing.Processor]
    if sys.stderr.isatty():
        processors = shared_processors + [structlog.dev.ConsoleRenderer()]
    else:
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(serializer=orjson.dumps),
        ]

    structlog.configure(
        cache_logger_on_first_use=True,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        processors=processors,
        # logger_factory=structlog.BytesLoggerFactory(),
    )
