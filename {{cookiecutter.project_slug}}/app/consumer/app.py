from infrastructure.ioc.container import Container
from infrastructure.kafka.app import create_consumer_app

Container()
app = create_consumer_app()
