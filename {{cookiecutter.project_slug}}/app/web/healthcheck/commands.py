from abc import ABC, abstractmethod

from dependency_injector.wiring import Closing, Provide
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from utils.time import TimeCatcher
from web.healthcheck.status import Status


class CommandResult(BaseModel):
    status: Status
    data: dict = Field(default_factory=dict)
    duration: float
    exception: str | None = None
    description: str | None = None


class BaseCommand(ABC):
    @abstractmethod
    async def execute(self) -> CommandResult:
        """
        Запуск проверки сервиса
        :return:
        """
        ...


class DBCommand(BaseCommand):
    def __init__(self, db_session: AsyncSession = Closing[Provide["db_session"]]):
        self.db_session = db_session

    async def execute(self) -> CommandResult:
        async with TimeCatcher() as catcher:
            try:
                await self.db_session.execute(select("1"))
                status, exception, description = Status.HEALTHY, None, None
            except SQLAlchemyError as e:
                status, exception, description = Status.UNHEALTHY, str(type(e)), str(e)

        return CommandResult(
            status=status,
            duration=catcher.total_duration,
            exception=exception,
            description=description,
        )
