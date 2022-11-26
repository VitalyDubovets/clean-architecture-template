import uuid
from typing import Any, Callable, Coroutine, Optional

from fastapi import FastAPI, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import ExpiredSignatureError, JWTError, jwt
from opentelemetry import trace
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.middleware.cors import CORSMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars

from core.dto.auth import UserDTO
from core.errors import SecurityBusinessError
from infrastructure.config import KeycloakConfig, config
from infrastructure.sentry import configure_sentry
from web.errors import HTTPCustomError

tracer = trace.get_tracer(__name__)


class RolesKeycloakMiddleware(HTTPBearer):
    """
    Middleware для проверки доступа пользователя до конкретного endpoint
    """

    def __init__(
        self,
        *,
        roles: list[str],
        keycloak_config: KeycloakConfig = config.KEYCLOAK_CONFIG,
        bearer_format: str = "Bearer",
        scheme_name: Optional[str] = "Authorization",
        description: Optional[str] = "Авторизация по JWT токену",
        auto_error: bool = True,
    ):
        super().__init__(
            bearerFormat=bearer_format, scheme_name=scheme_name, description=description, auto_error=auto_error
        )
        self._roles = roles
        self._config = keycloak_config

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        with tracer.start_as_current_span("RolesKeycloakMiddleware.__call__"):
            token = await self._get_token_from_authorization_scheme(request)

            try:
                token_payload = self._receive_token_payload(token.credentials)
            except (ExpiredSignatureError, JWTError) as e:
                raise HTTPCustomError(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=str(e),
                    business_error=SecurityBusinessError(
                        status="401",
                        detail=str(e),
                    ),
                ) from e

            roles = self._get_roles_from_token_payload(token_payload)

            if not self._check_user_access_roles(roles):
                raise HTTPCustomError(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                    business_error=SecurityBusinessError(
                        status="403",
                        detail="Not enough permissions",
                    ),
                )

            request.state.user = UserDTO.parse_obj(token_payload)

            return token

    async def _get_token_from_authorization_scheme(self, request: Request) -> HTTPAuthorizationCredentials:
        with tracer.start_as_current_span("RolesKeycloakMiddleware._get_token_from_authorization_scheme"):
            authorization: str = request.headers.get("Authorization")
            scheme, credentials = get_authorization_scheme_param(authorization)

            if not (authorization and scheme and credentials):
                if self.auto_error:
                    raise HTTPCustomError(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Not authenticated",
                        business_error=SecurityBusinessError(
                            status="403",
                            detail="Not authenticated",
                        ),
                    )
            if scheme.lower() != "bearer":
                if self.auto_error:
                    raise HTTPCustomError(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Invalid authentication credentials",
                        business_error=SecurityBusinessError(
                            status="403",
                            detail="Invalid authentication credentials",
                        ),
                    )

            return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)

    def _receive_token_payload(self, token: str) -> dict:
        """
        Получение payload токена

        :param token: JWT
        :return: token payload
        :raise: ExpiredSignatureError, JWTError
        """
        with tracer.start_as_current_span("RolesKeycloakMiddleware._receive_token_payload"):
            return jwt.decode(
                token=token,
                key=self._config.PUBLIC_KEY,
                algorithms=self._config.ALGORITHMS,
                audience=self._config.CLIENT_ID,
                options={"verify_aud": False},
            )

    def _get_roles_from_token_payload(self, token_payload: dict) -> list[str]:
        """
        Получить keycloak роли пользователя из JWT payload

        :param token_payload: JWT payload
        :return: Список ролей
        """
        with tracer.start_as_current_span("RolesKeycloakMiddleware._get_roles_from_token_payload"):
            realm_access = token_payload.get("realm_access", {})
            resource_access = token_payload.get("resource_access", {})
            client_access = resource_access.get(self._config.CLIENT_ID, {})

            client_roles = client_access.get("roles", []) if client_access is not None else []
            realm_roles = realm_access.get("roles", []) if realm_access is not None else []

            return client_roles + realm_roles

    def _check_user_access_roles(self, roles: list[str]) -> bool:
        """
        Проверка доступов пользователя

        :param roles: Роли пользователя
        :return: Результат проверки доступа
        """
        with tracer.start_as_current_span("RolesKeycloakMiddleware._check_user_access_roles"):
            return set(self._roles).issubset(set(roles))


def register_middleware(app: FastAPI) -> None:
    """
    Фукнция для регистрации глобальных middlewares

    :param app: Приложение FastAPI
    :return:
    """
    with tracer.start_as_current_span("register_middlewares"):
        if config.SENTRY_CONFIG.DSN is not None:
            configure_sentry(dsn=config.SENTRY_CONFIG.DSN, environment=config.SENTRY_CONFIG.STAGE)
            app.add_middleware(SentryAsgiMiddleware)

        @app.middleware("http")
        async def add_request_id(request: Request, call_next: Callable[[Any], Coroutine]) -> Response:
            """
            Middleware для трассировки запроса

            :param request: Endpoint mock_request
            :param call_next: Следующий вызов
            :return:
            """
            clear_contextvars()
            bind_contextvars(x_correlation_id=str(uuid.uuid4()))

            response: Response = await call_next(request)

            return response

        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.CORS_CONFIG.ORIGINS,
            allow_credentials=True,
            allow_methods=config.CORS_CONFIG.METHODS,
            allow_headers=config.CORS_CONFIG.HEADERS,
        )
