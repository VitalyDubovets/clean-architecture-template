from typing import Generic, TypeVar

from pydantic.generics import GenericModel

from core.usecases.base import BaseResult, CustomModel

ResultType = TypeVar("ResultType", bound=BaseResult)


class PaginationQuery(CustomModel):
    offset: int
    limit: int


class PageInfo(CustomModel):
    page_number: int
    page_size: int


class PaginationResult(GenericModel, CustomModel, Generic[ResultType]):
    items: list[ResultType]
    total_count: int
    page: PageInfo
