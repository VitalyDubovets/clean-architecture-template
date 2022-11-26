from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Union

from core.usecases.base import BaseQuery, BaseResult

TQuery = TypeVar("TQuery", bound=BaseQuery)
TResult = TypeVar("TResult", bound=Union[BaseResult, list[BaseResult]])


class IQueryHandler(Generic[TQuery, TResult], ABC):
    @abstractmethod
    async def ask(self, query: TQuery) -> TResult:
        ...
