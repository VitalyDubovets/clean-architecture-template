from abc import ABC, abstractmethod
from typing import Optional

import orjson
import structlog
from httpx import AsyncClient, Response
from jose import jwt
from tests.utils import curlify

from infrastructure.config import KeycloakConfig


class UserAPIClient(ABC):
    """
    Базовый класс пользовательского API client
    """

    def __init__(self, client: AsyncClient, config: KeycloakConfig):
        self._client = client
        self._config = config
        self._algorithm = "RS256"
        self._logger = structlog.get_logger()

    @property
    @abstractmethod
    def fresh_jwt_payload(self):
        ...

    @property
    @abstractmethod
    def rotten_jwt_payload(self):
        ...

    def get_jwt_token(self, payload: dict) -> str:
        return jwt.encode(payload, self._config.PUBLIC_KEY)

    def create_auth_header_by_jwt_payload(self, jwt_payload: Optional[dict] = None) -> dict:
        if jwt_payload is not None:
            headers = {"Authorization": f"Bearer {self.get_jwt_token(jwt_payload)}"}
        else:
            headers = {}

        return headers

    async def request(
        self,
        url: str,
        *,
        method: str = "GET",
        api_version: str = "/v1",
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
        **kwargs,
    ) -> Response:
        return await self._request(
            url=url,
            method=method,
            api_version=api_version,
            json=json,
            headers=headers,
            data=data,
            params=params,
            **kwargs,
        )

    async def _request(
        self,
        url: str,
        *,
        method: str = "GET",
        api_version: str = "/v1",
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
        **kwargs,
    ) -> Response:
        if headers is None:
            headers = {
                "Authorization": f"Bearer {self.get_jwt_token(self.fresh_jwt_payload)}",
            }

        if headers.get("Content-Type", None) is None:
            headers["Content-Type"] = "application/json"

        response = await self._client.request(
            method, f"{api_version}{url}", headers=headers, json=json, timeout=30, data=data, params=params, **kwargs
        )

        if response.is_success:
            self._logger.info(
                "✅ Got response",
                method=method,
                url=url,
                status_code=response.status_code,
            )

            self._logger.debug("🤩 ➡️ mock_request curl", curl=curlify.to_curl(response.request))
            if response.text:
                try:
                    self._logger.debug(
                        "🤩 response body",
                        json=orjson.dumps(response.json(), option=orjson.OPT_INDENT_2),
                    )
                except ValueError:
                    self._logger.debug("🤩 response body", body=response.text)

        elif response.is_client_error:
            self._logger.info(
                "🙈 Got bad response",
                method=method,
                url=url,
                status_code=response.status_code,
            )
            self._logger.debug("🤔 ➡️ bad mock_request curl", curl=curlify.to_curl(response.request))
            if response.text:
                try:
                    self._logger.debug(
                        "🤔 bad response body",
                        json_data=orjson.dumps(response.json(), option=orjson.OPT_INDENT_2),
                    )
                except ValueError:
                    self._logger.debug("🤔 bad response body", body=response.text)
        else:
            self._logger.error(
                "🆘 Internal server error",
                method=method,
                url=url,
                status_code=response.status_code,
                curl=curlify.to_curl(response.request),
            )
            self._logger.error("😱 ➡️ Error mock_request curl", curl=curlify.to_curl(response.request))
            if response.text:
                try:
                    self._logger.error(
                        "😱 error response body",
                        json_data=orjson.dumps(response.json(), option=orjson.OPT_INDENT_2),
                    )
                except ValueError:
                    self._logger.error("😱 error response body", body=response.text)

        return response
