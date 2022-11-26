from typing import AsyncGenerator

import structlog
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from infrastructure.config import config

logger = structlog.get_logger(__name__)

_async_engine: AsyncEngine = create_async_engine(config.POSTGRES_CONFIG.URI, echo=config.DEBUG, pool_pre_ping=True)
SQLAlchemyInstrumentor().instrument(engine=_async_engine.sync_engine)

_async_session = sessionmaker(
    autocommit=False, autoflush=True, bind=_async_engine, expire_on_commit=False, class_=AsyncSession
)


async def init_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with _async_session() as session:
        yield session
