DEFAULT_LOGGING_CONFIG: dict = {  # type: ignore
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "access": {
            "()": "logging.Formatter",
            "format": "%(t)s - %(client_addr)s - %(request_line)s",
        },
    },
    "handlers": {
        "access": {"formatter": "access", "class": "logging.StreamHandler"},
    },
    "loggers": {
        "aster.access": {"level": "INFO", "handlers": ["access"], "propagate": False},
    },
}
