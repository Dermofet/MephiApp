from typing import List

from redis.client import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.api.database.facade import FacadeDB, IFacadeDB
from logging_.logger import Logger


class BaseLoader:
    redis_db: Redis
    facade_db: IFacadeDB

    logger: Logger

    __engine: AsyncEngine
    __async_session: sessionmaker

    def __init__(
            self,
            redis_host: str,
            redis_port: int,
            redis_db: int,
            postgres_dsn: str,
            single_connection_client: bool = True,
            is_logged: bool = True,
            debug: bool = False,
    ):
        self.redis_db = Redis(host=redis_host, port=redis_port, db=redis_db, single_connection_client=single_connection_client)
        self.logger = Logger(is_logged)

        self.__engine = create_async_engine(
            postgres_dsn,
            echo=debug,
        )
        self.__async_session = sessionmaker(
            self.__engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    async def init_facade(self):
        session = self.__async_session()
        self.facade_db = FacadeDB(session)

    def __del__(self):
        self.__async_session.close_all()
