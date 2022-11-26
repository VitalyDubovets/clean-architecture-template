import logging
import logging.config
import sys
from enum import Enum

import orjson
import structlog
from structlog.contextvars import merge_contextvars


class LogFormat(str, Enum):
    JSON = "json"
    PLAIN = "plain"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def configure_logging(log_level: LogLevel = LogLevel.INFO, log_format: LogFormat = LogFormat.JSON):
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    pre_chain = [
        # Add the log level and a timestamp to the event_dict if the log entry
        # is not from structlog.
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        timestamper,
    ]

    if log_format == LogFormat.JSON:
        pre_chain.append(structlog.processors.format_exc_info)

    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=log_level.value)

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                LogFormat.PLAIN: {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.dev.ConsoleRenderer(colors=True),
                    ],
                    "foreign_pre_chain": pre_chain,
                },
                LogFormat.JSON: {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.processors.JSONRenderer(serializer=orjson.dumps),
                    "foreign_pre_chain": pre_chain,
                },
            },
            "handlers": {
                "default": {
                    "level": log_level.value,
                    "class": "logging.StreamHandler",
                    "formatter": log_format.value,
                },
            },
            "loggers": {
                "": {
                    "handlers": [
                        "default",
                    ],
                    "level": log_level.value,
                    "propagate": True,
                },
            },
        }
    )

    pre_chain.insert(0, merge_contextvars)

    structlog.configure(
        processors=pre_chain
        + [
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
