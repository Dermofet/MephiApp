import asyncio
import inspect

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.database.connection import Base
from tests.settings import settings


@pytest.fixture(scope="module")
def engine() -> AsyncEngine:
    return create_async_engine(settings.dsn, echo=False)


@pytest.fixture(scope="function")
async def session(engine) -> AsyncSession:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
