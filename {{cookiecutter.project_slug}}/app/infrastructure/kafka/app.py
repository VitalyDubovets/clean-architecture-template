from typing import Optional

import structlog
from faust import App, SASLCredentials

from infrastructure.config import config
from infrastructure.kafka.registry import register_consumer_schemas
from infrastructure.log import configure_logging
from infrastructure.sentry import configure_sentry
from infrastructure.tracing import FaustTracer

logger = structlog.get_logger(__name__)


def create_consumer_app() -> App:
    configure_logging(log_level=config.LOG.LEVEL, log_format=config.LOG.FORMAT)

    if config.SENTRY_CONFIG.DSN is not None:
        configure_sentry(dsn=config.SENTRY_CONFIG.DSN, environment=config.SENTRY_CONFIG.STAGE)

    register_consumer_schemas()

    credentials: Optional[SASLCredentials] = (
        SASLCredentials(
            username=config.KAFKA_CONFIG.USER,
            password=config.KAFKA_CONFIG.PASSWORD,
            mechanism=config.KAFKA_CONFIG.SASL_MECHANISMS,
        )
        if not config.KAFKA_CONFIG.LOCAL
        else None
    )

    logger.info("Consumer is being started...")
    app = App(
        id=f"consumer_{config.KAFKA_CONFIG.GROUP_ID}",
        broker=f"kafka://{config.KAFKA_CONFIG.BOOTSTRAP_SERVERS}",
        broker_credentials=credentials,
        autodiscover=True,
        origin="consumer",
        consumer_auto_offset_reset=config.KAFKA_CONFIG.AUTO_OFFSET_RESET,
        value_serializer="json",
    )
    app.tracer = FaustTracer(config=config)

    logger.info("Consumer was started!")

    return app


def create_producer_app() -> App:
    credentials = (
        SASLCredentials(
            username=config.KAFKA_CONFIG.USER,
            password=config.KAFKA_CONFIG.PASSWORD,
            mechanism=config.KAFKA_CONFIG.SASL_MECHANISMS,
        )
        if not config.DEBUG
        else None
    )

    logger.info("A producer is being started...")
    app = App(
        id=f"consumer_{config.KAFKA_CONFIG.GROUP_ID}",
        broker=f"kafka://{config.KAFKA_CONFIG.BOOTSTRAP_SERVERS}",
        broker_credentials=credentials,
        autodiscover=True,
        origin="consumer",
    )
    app.producer_only = True
    app.tracer = FaustTracer(config=config)

    logger.info("The producer was started!")

    yield app

    logger.info("Closing a producer client...")
    app.stop()
    logger.info("The producer was closed!")
