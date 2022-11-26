from fastapi import APIRouter, Depends, FastAPI, status
from fastapi.datastructures import Default
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from opentelemetry import trace

from infrastructure.config import HealthCheckConfig
from web.healthcheck.commander import HealthCheckCommander, WorkingCapacityResult
from web.healthcheck.handler import CommandHandler
from web.healthcheck.status import Status

tracer = trace.get_tracer(__name__)


def register_healthcheck(app: FastAPI, healthcheck_config: HealthCheckConfig) -> None:
    with tracer.start_as_current_span("register_healthcheck"):
        healthcheck_router = APIRouter(prefix="/health", tags=["Healthcheck"])

        liveness_command_handler = CommandHandler()
        readiness_command_handler = CommandHandler()
        monitor_command_handler = CommandHandler()

        # TODO Need to implement your Command classes. Example:
        # liveness_command_handler.add_healthcheck_command(command=kafka_command)
        # readiness_command_handler.add_healthcheck_command(command=kafka_command)
        # monitor_command_handler.add_healthcheck_command(command=kafka_command)

        healthcheck_commander = HealthCheckCommander(
            liveness_handler=liveness_command_handler,
            readiness_handler=readiness_command_handler,
            monitor_handler=monitor_command_handler,
            healthcheck_config=healthcheck_config,
        )

        @healthcheck_router.get("/liveness", status_code=status.HTTP_200_OK, response_model=WorkingCapacityResult)
        async def liveness(result: WorkingCapacityResult = Depends(healthcheck_commander.run_liveness_route)):
            with tracer.start_as_current_span("liveness"):
                if result.status == Status.HEALTHY:
                    return result
                else:
                    return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(result))

        @healthcheck_router.get("/readiness", status_code=status.HTTP_200_OK, response_model=WorkingCapacityResult)
        async def readiness(result: WorkingCapacityResult = Depends(healthcheck_commander.run_readiness_route)):
            with tracer.start_as_current_span("readiness"):
                if result.status == Status.HEALTHY:
                    return result
                else:
                    return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(result))

        @healthcheck_router.get("/monitor", status_code=status.HTTP_200_OK, response_model=WorkingCapacityResult)
        async def monitor(result: WorkingCapacityResult = Depends(healthcheck_commander.run_monitor_route)):
            with tracer.start_as_current_span("monitor"):
                if result.status == Status.HEALTHY:
                    return result
                else:
                    return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=jsonable_encoder(result))

        app.include_router(healthcheck_router, default_response_class=Default(ORJSONResponse))
