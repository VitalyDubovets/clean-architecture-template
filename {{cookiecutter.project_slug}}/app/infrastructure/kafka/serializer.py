from dependency_injector.wiring import Provide, inject
from schema_registry.client import SchemaRegistryClient
from schema_registry.client.schema import JsonSchema
from schema_registry.serializers.faust import FaustJsonSerializer

from infrastructure.config import config


# TODO: Удалить после реализации бизнес сериалайзеров
@inject
def get_sample_serializer(client: SchemaRegistryClient = Provide["kafka.registry_client"]) -> FaustJsonSerializer:
    test_schema: JsonSchema = client.get_by_id(config.KAFKA_CONFIG.SCHEMA_TEST_ID)
    return FaustJsonSerializer(client, config.KAFKA_CONFIG.SCHEMA_TEST_SUBJECT, test_schema.schema)
