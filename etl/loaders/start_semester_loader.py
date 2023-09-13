from etl.loaders.base_loader import BaseLoader
from etl.schemas.start_semester import StartSemesterLoading


class StartSemesterLoader(BaseLoader):
    def __init__(
            self,
            redis_host: str,
            redis_port: int,
            redis_db: int,
            postgres_dsn: str,
            single_connection_client: bool = True,
            is_logged: bool = True,
            debug: bool = False
    ):
        super().__init__(redis_host, redis_port, redis_db, postgres_dsn, single_connection_client, is_logged, debug)

    async def load(self):
        self.logger.info("Loading start semester date...")

        try:
            await self.__load_start_semester()
            await self.facade_db.commit()
        except Exception as e:
            self.logger.error(f"Can't loading data: {e}")
            await self.facade_db.rollback()

        self.logger.info("Start semester date loaded successfully")

    async def __load_start_semester(self):
        date_ = StartSemesterLoading.model_validate_redis(self.redis_db.get("start_semester"))

        if await self.facade_db.get_start_semester() is None:
            await self.facade_db.create_start_semester(date_)
        else:
            await self.facade_db.update_start_semester(date_)

        self.redis_db.delete("start_semester")

        self.logger.debug("Start semester date are loaded")