from opentelemetry import trace

from infrastructure.config import HealthCheckConfig
from utils.time import TimeCatcher
from web.dto.base import BaseCamelCaseModel
from web.healthcheck.commands import BaseCommand
from web.healthcheck.handler import CommandHandler
from web.healthcheck.status import Status

tracer = trace.get_tracer(__name__)


class WorkingCapacityResult(BaseCamelCaseModel):
    status: Status
    total_duration: float
    entries: dict[str, dict]


class HealthCheckCommander:
    __slots__ = ("_liveness_handler", "_readiness_handler", "_monitor_handler", "_config")

    def __init__(
            self,
            liveness_handler: CommandHandler,
            readiness_handler: CommandHandler,
            monitor_handler: CommandHandler,
            healthcheck_config: HealthCheckConfig,
    ) -> None:
        self._liveness_handler = liveness_handler
        self._readiness_handler = readiness_handler
        self._monitor_handler = monitor_handler
        self._config = healthcheck_config

    async def run_liveness_route(self) -> WorkingCapacityResult:
        """
        Эндпоинт для проверки liveness

        :return: Результат проверки
        """
        with tracer.start_as_current_span("run_liveness_route"):
            return await self._form_working_capacity(
                self._liveness_handler, need_percentage=self._config.PERCENTAGE_MINIMUM_FOR_WORKING_CAPACITY
            )

    async def run_readiness_route(self) -> WorkingCapacityResult:
        """
        Эндпоинт для проверки readiness

        :return: Результат проверки
        """
        with tracer.start_as_current_span("run_readiness_route"):
            return await self._form_working_capacity(
                self._readiness_handler, need_percentage=self._config.PERCENTAGE_MINIMUM_FOR_WORKING_CAPACITY
            )

    async def run_monitor_route(self) -> WorkingCapacityResult:
        """
        Эндпоинт для проверки monitor

        :return: Результат проверки
        """
        with tracer.start_as_current_span("run_monitor_route"):
            return await self._form_working_capacity(
                self._monitor_handler, need_percentage=self._config.PERCENTAGE_MAXIMUM_FOR_WORKING_CAPACITY
            )

    async def _form_working_capacity(
            self, command_handler: CommandHandler, need_percentage: float
    ) -> WorkingCapacityResult:
        """
        Формирование результата проверки на работоспособность сервисов

        :param command_handler: перехватчик команд
        :param need_percentage: нужны процент работоспособности сервисов
        :return: Result of working capacity
        """
        with tracer.start_as_current_span("_form_working_capacity"):
            count_healthy_services = 0
            entries = dict()

            async with TimeCatcher() as catcher:  # type: TimeCatcher
                for name, command in command_handler.commands:  # type: str, BaseCommand
                    command_result = await command.execute()

                    if command_result.status == Status.HEALTHY:
                        count_healthy_services += 1

                    entries[name] = command_result.dict(exclude_none=True)

            if self._is_services_healthy(
                    count_healthy_services=count_healthy_services,
                    count_all_services=len(command_handler.commands),
                    need_percentage=need_percentage,
            ):
                status = Status.HEALTHY
            else:
                status = Status.UNHEALTHY

            return WorkingCapacityResult(status=status, total_duration=catcher.total_duration, entries=entries)

    @staticmethod
    def _is_services_healthy(*, count_healthy_services: int, count_all_services: int, need_percentage: float) -> bool:
        """
        Проверка работоспособности сервисов на основе результатов

        :param count_healthy_services: Количество здоровых сервисов
        :param count_all_services: Количество всех сервисов
        :return: Результат проверка состояния
        """
        with tracer.start_as_current_span("_is_services_healthy"):
            return (
                (count_healthy_services / count_all_services * 100) >= need_percentage
                if count_all_services != 0
                else count_all_services >= need_percentage
            )
