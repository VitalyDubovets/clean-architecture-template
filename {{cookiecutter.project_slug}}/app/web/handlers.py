from enum import Enum
from itertools import starmap
from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from humps import camelize
from opentelemetry import trace
from pydantic import ValidationError
from starlette.responses import JSONResponse

from core.errors import BaseBusinessError, ErrorCategories, UnexpectedBusinessError, ValidationBusinessError
from web.errors import HTTPCustomError

logger = structlog.getLogger(__name__)
tracer = trace.get_tracer(__name__)


def _camelize_dict_factory(result: list[tuple[str, Any]]) -> dict:
    with tracer.start_as_current_span("_camelize_dict_factory"):
        return dict(
            starmap(lambda key, value: (camelize(key), value.value if isinstance(value, Enum) else value), result)
        )


def _as_camelized_dict(exc: BaseBusinessError) -> dict:
    with tracer.start_as_current_span("_as_camelized_dict"):
        return dict(_camelize_dict_factory(exc.as_dict().items()))


def register_error_handlers(app: FastAPI) -> FastAPI:
    with tracer.start_as_current_span("_register_error_handlers"):
        app.add_exception_handler(HTTPCustomError, http_business_error_handler)
        app.add_exception_handler(RequestValidationError, http_validation_error_handler)
        app.add_exception_handler(ValidationError, http_validation_error_handler)
        app.add_exception_handler(Exception, http_internal_server_error_handler)
        return app


async def http_business_error_handler(_: Request, exc: HTTPCustomError) -> JSONResponse:
    with tracer.start_as_current_span("http_business_error_handler"):
        logger.info(exc)
        return ORJSONResponse(status_code=exc.status_code, content=_as_camelized_dict(exc.business_error))


async def http_validation_error_handler(_: Request, exc: ValidationError) -> JSONResponse:
    with tracer.start_as_current_span("http_validation_error_handler"):
        logger.info(exc)
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_as_camelized_dict(
                ValidationBusinessError(
                    status="422",
                    detail=str(exc),
                    data={"errors": exc.errors()},
                    raw_type=exc.__class__.__name__,
                    category=ErrorCategories.VALIDATION_EXCEPTION,
                )
            ),
        )


async def http_internal_server_error_handler(_: Request, exc: Exception) -> JSONResponse:
    with tracer.start_as_current_span("http_internal_server_error_handler"):
        logger.error(exc)
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_as_camelized_dict(
                UnexpectedBusinessError(
                    status="500",
                    detail=str(exc),
                    raw_type=exc.__class__.__name__,
                    category=ErrorCategories.UNEXPECTED_EXCEPTION,
                )
            ),
        )
