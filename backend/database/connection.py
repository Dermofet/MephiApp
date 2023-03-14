from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import DropTable

from backend.config.config import get_config

config = get_config()
engine = create_async_engine(
    config.SQLALCHEMY_DATABASE_URI,
    echo=config.DEBUG,
    pool_size=20,
    max_overflow=30,
    pool_timeout=60
)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


async def get_session() -> AsyncSession:
    print(config.SQLALCHEMY_DATABASE_URI)
    async with async_session() as session:
        return session


async def init_db() -> None:
    async with engine.begin() as connect:
        # await connect.run_sync(Base.metadata.drop_all)
        await connect.run_sync(Base.metadata.create_all)
