from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import config

engine = create_async_engine(
    config.DB_URI.unicode_string(),
    echo=config.DEBUG,
)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    __allow_unmapped__ = True

    metadata = MetaData()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
        