from redis import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from backend.api.database.facade import FacadeDB, IFacadeDB
from logging_.logger import Logger
from utils import asyncio


class BaseLoader:
    redis_db: Redis
    facade_db: IFacadeDB

    logger: Logger

    __engine: AsyncEngine
    __async_session: async_sessionmaker
    session: AsyncSession

    def __init__(
        self,
        redis: str,
        postgres_dsn: str,
        single_connection_client: bool = True,
        is_logged: bool = True,
        debug: bool = False,
    ):
        self.redis_db = Redis.from_url(redis, single_connection_client=single_connection_client)
        self.logger = Logger(is_logged)

        self.__engine = create_async_engine(
            postgres_dsn,
            echo=debug,
            pool_pre_ping=True,
            pool_recycle=1800,
        )
        self.__async_session = async_sessionmaker(
            self.__engine, expire_on_commit=False, class_=AsyncSession, autoflush=False
        )

    def init_facade(self):
        self.session = self.__async_session()
        self.facade_db = FacadeDB(self.session, version="0.0.1")

    def __del__(self):
        asyncio.run(self.session.close())
        self.redis_db.close()


class WrapperBaseLoader:
    loader: BaseLoader

    def __init__(
        self,
        url: str,
        redis: str,
        postgres_dsn: str,
        auth_url: str = None,
        auth_service_url: str = None,
        login: str = None,
        password: str = None,
        use_auth: bool = True,
        single_connection_client: bool = True,
        debug: bool = False,
        is_logged: bool = True,
    ):
        super().__init__(
            url=url,
            redis=redis,
            auth_url=auth_url,
            auth_service_url=auth_service_url,
            login=login,
            password=password,
            use_auth=use_auth,
            single_connection_client=single_connection_client,
            is_logged=is_logged,
        )
        self.loader = BaseLoader(
            redis=redis,
            postgres_dsn=postgres_dsn,
            single_connection_client=single_connection_client,
            is_logged=is_logged,
            debug=debug,
        )
        self.loader.init_facade()
