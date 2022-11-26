import sentry_sdk
import structlog


def configure_sentry(dsn: str, environment: str):
    logger = structlog.get_logger(__name__)
    if dsn is None:
        raise ValueError("Sentry dsn is empty")

    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        attach_stacktrace=True,
        request_bodies="always",
        with_locals=True,
    )
    logger.info("Configured sentry")
