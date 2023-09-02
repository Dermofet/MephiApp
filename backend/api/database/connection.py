from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import DropTable

from backend.config import config

engine = create_async_engine(
    config.SQLALCHEMY_DATABASE_URI,
    echo=config.DEBUG,
    pool_size=20,
    max_overflow=30,
    pool_timeout=60,
    pool_recycle=900,
    pool_pre_ping=True
)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return f"{compiler.visit_drop_table(element)} CASCADE"


async def get_session_yield() -> AsyncSession:
    async with async_session() as session:
        yield session


async def get_session_return() -> AsyncSession:
    async with async_session() as session:
        return session


async def init_db() -> None:
    async with engine.begin() as connect:
        # await connect.run_sync(Base.metadata.drop_all)
        await connect.run_sync(Base.metadata.create_all)