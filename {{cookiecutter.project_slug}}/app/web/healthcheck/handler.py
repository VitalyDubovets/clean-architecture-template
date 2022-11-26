import structlog
from opentelemetry import trace

from web.healthcheck.commands import BaseCommand

logger = structlog.get_logger(__name__)
tracer = trace.get_tracer(__name__)


class CommandHandler:
    __slots__ = ("_commands",)

    def __init__(self):
        self._commands: dict[str, BaseCommand] = dict()

    def add_healthcheck_command(self, service_name: str, command: BaseCommand) -> None:
        """
        Добавление команды с проверкой сервиса
        :param service_name: Имя сервиса
        :param command: Команда проверки сервиса
        :return:
        """
        with tracer.start_as_current_span("add_healthcheck_command"):
            self._commands[service_name] = command

    @property
    def commands(self) -> dict[str, BaseCommand]:
        return self._commands
