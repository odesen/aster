import atexit
import logging
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from logging.handlers import QueueHandler, QueueListener
from queue import Queue
from typing import Any

import orjson
import structlog
from structlog.types import BindableLogger, FilteringBoundLogger, Processor, WrappedLogger


def default_structlog_processors() -> list[Processor]:
    return [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer(serializer=orjson.dumps),
    ]


def default_structlog_wrapper_class() -> type[BindableLogger] | None:
    return structlog.make_filtering_bound_logger(logging.INFO)


def default_logger_factory() -> Callable[..., WrappedLogger] | None:
    return structlog.BytesLoggerFactory()


@dataclass
class StructLoggingConfig:
    """Configuration class for structlog.
    Notes:
        - requires 'structlog' to be installed.
    """

    processors: list[Processor] | None = field(default_factory=default_structlog_processors)
    """Iterable of structlog logging processors."""
    wrapper_class: type[BindableLogger] | None = field(
        default_factory=default_structlog_wrapper_class
    )
    """Structlog bindable logger."""
    context_class: dict[str, Any] | None = None
    """Context class (a 'contextvar' context) for the logger."""
    logger_factory: Callable[..., WrappedLogger] | None = field(
        default_factory=default_logger_factory
    )
    """Logger factory to use."""
    cache_logger_on_first_use: bool = field(default=True)
    """Whether to cache the logger configuration and reuse."""

    def configure(self) -> Callable[..., FilteringBoundLogger]:
        """Return logger with the given configuration.
        Returns:
            A 'logging.getLogger' like function.
        """
        try:
            from structlog import configure, get_logger

            # we now configure structlog
            configure(**dict(asdict(self).items()))
            return get_logger
        except ImportError as e:  # pragma: no cover
            raise e


def resolve_handlers(handlers: list[Any]) -> list[Any]:
    return [handlers(i) for i in range(len(handlers))]  # type: ignore


class QueueListenerHandler(QueueHandler):
    def __init__(self, handlers: list[Any] | None = None) -> None:
        super().__init__(Queue(-1))
        handlers = resolve_handlers(handlers) if handlers else [logging.StreamHandler()]
        self.listener = QueueListener(self.queue, *handlers)
        self.listener.start()

        atexit.register(self.listener.stop)
