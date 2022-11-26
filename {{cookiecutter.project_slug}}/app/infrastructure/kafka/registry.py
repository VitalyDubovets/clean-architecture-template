from faust.serializers import codecs

from infrastructure.kafka.serializer import get_sample_serializer


def register_consumer_schemas() -> None:
    codecs.register("json_testing", get_sample_serializer())
