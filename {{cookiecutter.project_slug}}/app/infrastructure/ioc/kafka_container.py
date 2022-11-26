from dependency_injector import containers, providers
from schema_registry.client import Auth, SchemaRegistryClient

from infrastructure.kafka.app import create_producer_app


class KafkaContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    producer_app = providers.Resource(create_producer_app)
    registry_client = providers.Singleton(
        SchemaRegistryClient,
        url=config.KAFKA_CONFIG.SCHEMA_REGISTRY_URL,
        ca_location=config.KAFKA_CONFIG.CA_LOCATION,
        auth=providers.Factory(
            Auth,
            username=config.KAFKA_CONFIG.SCHEMA_REGISTRY_USER,
            password=config.KAFKA_CONFIG.SCHEMA_REGISTRY_PASSWORD,
        )
        if not config.KAFKA_CONFIG.LOCAL
        else None,
    )
