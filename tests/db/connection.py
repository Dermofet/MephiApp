from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.database.connection import Base
from tests.settings import settings


def _engine() -> AsyncEngine:
    return create_async_engine(settings.dsn, echo=True)


async def get_session() -> AsyncSession:
    engine = _engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    return async_session()

async def get_db():
    async with get_session() as session:
        yield session
