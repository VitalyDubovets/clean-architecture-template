import faust


# TODO: Тестовый экземпляр. Когда будет добавлены продакшн топики, то следует удалить
class TestingJson(faust.Record, serializer="json_testing"):
    """
    Testing
    """
    id: int
    count: int
    description: str
