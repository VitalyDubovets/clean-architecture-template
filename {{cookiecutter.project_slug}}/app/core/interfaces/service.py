import abc
from typing import Generic, TypeVar

from pydantic import BaseModel

ClientResponse = TypeVar('ClientResponse', bound=BaseModel)


class IHTTPService(Generic[ClientResponse], metaclass=abc.ABCMeta):
    @property
    def http_headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @abc.abstractmethod
    async def request(
        self,
        *,
        method: str,
        url: str,
        headers: dict = None,
        **kwargs
    ) -> ClientResponse:
        """
        Выполнить http запрос
        :param method: http-метод (get, post, put, patch …)
        :param url: ресурс к которму необходимо обратиться
        :param headers: http-заголовки
        :param kwargs:
        :return: ClientResponse
        """
        ...
