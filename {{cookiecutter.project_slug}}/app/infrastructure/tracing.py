from typing import Any, ContextManager, Optional

from fastapi import FastAPI
from faust.types.app import TracerT  # noqa
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import SERVICE_INSTANCE_ID, SERVICE_NAME, SERVICE_NAMESPACE, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from infrastructure.config import Config

{% if cookiecutter.use_kafka == 'yes' %}
from opentelemetry.shim.opentracing_shim import TracerShim
{% endif %}

def init_tracing(config: Config) -> TracerProvider:
    resource = Resource(
        attributes={
            SERVICE_NAME: config.PROJECT_NAME,
            SERVICE_NAMESPACE: config.TRACING_CONFIG.NAMESPACE,
            SERVICE_INSTANCE_ID: config.TRACING_CONFIG.INSTANCE_ID,
            SERVICE_VERSION: config.TRACING_CONFIG.VERSION,
        }
    )
    tracer = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer)
    tracer.add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=config.TRACING_CONFIG.JAEGER_HOST,
                agent_port=config.TRACING_CONFIG.JAEGER_PORT,
            )
        )
    )
    LoggingInstrumentor().instrument()

    return tracer


def init_tracing_for_app(app: FastAPI, config: Config) -> TracerProvider:
    tracer = init_tracing(config=config)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)

    return tracer

{% if cookiecutter.use_kafka == 'yes' %}
class FaustTracer(TracerT):
    def __init__(self, config: Config):
        self._tracer = init_tracing(config)

    @property
    def default_tracer(self) -> TracerShim:
        return TracerShim(self._tracer.get_tracer(__name__))  # noqa

    def trace(self, name: str, _: Optional[float] = None, **__: Any) -> ContextManager:
        return TracerShim(self._tracer.get_tracer(name)).start_active_span(name, **extra_context)  # noqa

    def get_tracer(self, service_name: str) -> TracerShim:
        return TracerShim(self._tracer.get_tracer(service_name))  # noqa
{% endif %}