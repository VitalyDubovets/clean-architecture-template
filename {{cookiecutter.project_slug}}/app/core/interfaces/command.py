from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union

from core.usecases.base import BaseCommand, BaseCommandResult

TCommand = TypeVar("TCommand", bound=BaseCommand)
TResult = TypeVar("TResult", bound=Union[BaseCommandResult, None])


class ICommandHandler(Generic[TCommand, TResult], ABC):
    @abstractmethod
    async def execute(self, command: TCommand) -> TResult:
        ...
