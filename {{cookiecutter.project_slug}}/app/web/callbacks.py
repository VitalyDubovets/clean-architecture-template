from fastapi import FastAPI
from opentelemetry import trace

from infrastructure.ioc.container import Container

tracer = trace.get_tracer(__name__)


def register_callback(app: FastAPI, container: Container) -> None:
    with tracer.start_as_current_span("register_callback"):
        def shutdown():
            container.shutdown_resources()

        app.add_event_handler("shutdown", shutdown)
