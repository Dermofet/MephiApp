from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import config

engine = create_async_engine(
    config.DB_URI.unicode_string(),
    echo=config.DEBUG,
    pool_pre_ping=True,
    pool_recycle=1800,
)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession, autoflush=False)

class Base(DeclarativeBase):
    __allow_unmapped__ = True

    metadata = MetaData()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session