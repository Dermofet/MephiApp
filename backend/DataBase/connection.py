from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from backend.Config.config import get_config

config = get_config()
print(config.SQLALCHEMY_DATABASE_URI)
engine = create_async_engine(config.SQLALCHEMY_DATABASE_URI, echo=config.DEBUG)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as connect:
        await connect.run_sync(Base.metadata.drop_all)
        await connect.run_sync(Base.metadata.create_all)
