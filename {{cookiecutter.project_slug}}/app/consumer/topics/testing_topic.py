from typing import AsyncIterable

import structlog

from consumer.app import app
from consumer.dto.testing_variant import TestingJson

logger = structlog.get_logger(__name__)
topic = app.topic("test_topic", value_type=TestingJson)


@app.agent(topic)
async def iterate(testings: AsyncIterable[TestingJson]):
    async for testing in testings:
        logger.info("testing", value=testing.to_representation())
