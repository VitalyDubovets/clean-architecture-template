from dependency_injector import containers
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from infrastructure.config import config
from infrastructure.ioc.container import Container
from infrastructure.log import configure_logging
from infrastructure.tracing import init_tracing_for_app
from web.callbacks import register_callback
from web.handlers import register_error_handlers
from web.healthcheck.router import register_healthcheck
from web.middlewares import register_middleware


def create_app(container: containers.DeclarativeContainer = None) -> FastAPI:
    container = container or Container()
    application = FastAPI(
        debug=config.DEBUG,
        title=config.PROJECT_NAME,
        openapi_url="/openapi.json",
        default_response_class=ORJSONResponse,
    )
    register_middleware(application)
    register_error_handlers(application)
    register_healthcheck(app=application, healthcheck_config=config.HEALTHCHECK_CONFIG)
    register_callback(app=application, container=container)
    configure_logging(log_level=config.LOG.LEVEL, log_format=config.LOG.FORMAT)
    init_tracing_for_app(application, config)

    return application


fastapi_app = create_app()
