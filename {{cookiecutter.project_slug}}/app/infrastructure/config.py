import uuid
from typing import Any, Optional

from pydantic import AnyUrl, BaseSettings, Extra, HttpUrl, validator, Field

from infrastructure.log import LogLevel, LogFormat


class BaseProjectConfig(BaseSettings):
    class Config:
        case_sensitive = True
        extra = Extra.ignore

{% if cookiecutter.use_postgres == 'yes' %}

class _AsyncPostgresDsn(AnyUrl):
    allowed_schemes = {"postgres", "postgresql", "postgresql+asyncpg"}
    user_required = True


class PostgresConfig(BaseProjectConfig):
    HOST: str = "localhost"
    PORT: str = "5432"
    USER: str
    PASSWORD: str
    DB: str
    URI: Optional[_AsyncPostgresDsn] = None

    @validator("URI", pre=True, allow_reuse=True)
    def assemble_async_db_connection(cls, v: Optional[str], values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return _AsyncPostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("USER"),
            password=values.get("PASSWORD"),
            host=values.get("HOST"),
            port=values.get("PORT"),
            path=f"/{values.get('DB') or ''}",
        )

    class Config(BaseProjectConfig.Config):
        env_prefix = 'POSTGRES_'

{% endif %}
class CORSConfig(BaseProjectConfig):
    ORIGINS: list[str] = ["*"]
    METHODS: list[str] | str = ["*"]
    HEADERS: list[str] = ["*"]

    class Config(BaseProjectConfig.Config):
        env_prefix = 'CORS_'


class TracingConfig(BaseProjectConfig):
    JAEGER_HOST: Optional[str] = None
    JAEGER_PORT: Optional[int] = None
    NAMESPACE: str = "default"
    INSTANCE_ID: str = Field(default=str(uuid.uuid4()))
    VERSION: str = "1.0.0"

    class Config(BaseProjectConfig.Config):
        env_prefix = "TRACING_"


class LogConfig(BaseProjectConfig):
    LEVEL: LogLevel = LogLevel.INFO
    FORMAT: LogFormat = LogFormat.PLAIN

    class Config(BaseProjectConfig.Config):
        env_prefix = 'LOG_'


class SentryConfig(BaseProjectConfig):
    DSN: Optional[HttpUrl] = None
    STAGE: str

    class Config(BaseProjectConfig.Config):
        env_prefix = 'SENTRY_'

{% if cookiecutter.use_kafka == 'yes' %}
class KafkaConfig(BaseProjectConfig):
    LOCAL: bool = True
    BOOTSTRAP_SERVERS: str
    SASL_MECHANISMS: str = "SCRAM-SHA-512"
    USER: Optional[str] = None
    PASSWORD: Optional[str] = None
    AUTO_OFFSET_RESET: str = "earliest"
    GROUP_ID: str = "1"
    CA_LOCATION: Optional[str] = None
    SCHEMA_REGISTRY_URL: str = "https://test.com"
    SCHEMA_REGISTRY_USER: Optional[str] = None
    SCHEMA_REGISTRY_PASSWORD: Optional[str] = None

    # topics
    TOPIC_TEST: str

    # schemas
    SCHEMA_TEST_SUBJECT: str
    SCHEMA_TEST_ID: int

    class Config(BaseProjectConfig.Config):
        env_prefix = "KAFKA_"

{% endif %}
class HealthCheckConfig(BaseProjectConfig):
    PERCENTAGE_MINIMUM_FOR_WORKING_CAPACITY: float = 80.0
    PERCENTAGE_MAXIMUM_FOR_WORKING_CAPACITY: float = 100.0

    class Config:
        env_prefix = "HEALTHCHECK_"


class Config(BaseProjectConfig):
    PROJECT_NAME: str
    ENVIRONMENT: str = "dev"
    DEBUG: bool = False

    LOG: LogConfig = LogConfig()
    CORS_CONFIG: CORSConfig = CORSConfig()
    TRACING_CONFIG: TracingConfig = TracingConfig()
    HEALTHCHECK_CONFIG: HealthCheckConfig = HealthCheckConfig()
    SENTRY_CONFIG: SentryConfig = SentryConfig() {% if cookiecutter.use_kafka == 'yes' %}
    KAFKA_CONFIG: KafkaConfig = KafkaConfig()
{% endif %} {% if cookiecutter.use_postgres == 'yes' %}
    POSTGRES_CONFIG: PostgresConfig = PostgresConfig()
{% endif %}

config: Config = Config()
