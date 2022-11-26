from dependency_injector import containers, providers

from infrastructure.config import config
from infrastructure.db.session import init_db_session
from infrastructure.ioc.commands_container import CommandsContainer

{% if cookiecutter.use_kafka == 'yes' %}
from infrastructure.ioc.kafka_container import KafkaContainer {% endif %}
from infrastructure.ioc.queries_container import QueriesContainer


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(pydantic_settings=[config])
    wiring_config = containers.WiringConfiguration(
        packages=[
            "core",
            "web",
            "infrastructure.commands",
            "infrastructure.http", {% if cookiecutter.use_kafka == 'yes' %}
            "infrastructure.kafka", {% endif %}
            "infrastructure.queries",
        ]
    )
    {% if cookiecutter.use_postgres == 'yes' %}
    db_session = providers.Resource(init_db_session)
    {% endif %}

    queries = providers.Container(QueriesContainer)
    commands = providers.Container(CommandsContainer)
    {% if cookiecutter.use_kafka == 'yes' %}
    kafka = providers.Container(KafkaContainer, config=config)
    {% endif %}
