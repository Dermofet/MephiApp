from etl.loaders.base_loader import BaseLoader
from etl.schemas.academic import AcademicLoading
from etl.schemas.corps import CorpsLoading
from etl.schemas.lesson import LessonLoading
from etl.schemas.room import RoomLoading
from etl.schemas.teacher import TeacherLoading


class ScheduleLoader(BaseLoader):
    def __init__(
            self,
            redis_host: str,
            redis_port: int,
            redis_db: int,
            postgres_dsn: str,
            single_connection_client: bool = True,
            is_logged: bool = True,
    ):
        super().__init__(redis_host, redis_port, redis_db, postgres_dsn, single_connection_client, is_logged)

    async def load(self):
        self.logger.info("Loading schedule...")

        # try:
        await self.__load_academics()
        await self.__load_corps()
        await self.__load_rooms()
        await self.__load_teachers()
        await self.__load_lessons()
        # except Exception as e:
        #     self.logger.error(f"Can't loading data: {e}")
        #     await self.facade_db.rollback()

        self.logger.info("Schedule loaded successfully")

    async def __load_academics(self):
        academics = [
            AcademicLoading.model_validate_redis(self.redis_db.hget(name=key.decode("utf-8"), key="academic"))
            for key in self.redis_db.keys("academics:*")
        ]

        await self.facade_db.bulk_insert_academic(academics)
        await self.facade_db.commit()

        self.redis_db.delete("academics:*")

        self.logger.debug("Academics are loaded")

    async def __load_corps(self):
        corps = [
            CorpsLoading.model_validate_redis(self.redis_db.hget(name=key.decode("utf-8"), key="corp"))
            for key in self.redis_db.keys("corps:*")
        ]

        await self.facade_db.bulk_insert_corps(corps)
        await self.facade_db.commit()

        self.redis_db.delete("corps:*")

        self.logger.debug("Corps are loaded")

    async def __load_rooms(self):
        rooms = [
            RoomLoading.model_validate_redis(self.redis_db.hget(name=key.decode("utf-8"), key="room"))
            for key in self.redis_db.keys("rooms:*")
        ]

        await self.facade_db.bulk_insert_room(rooms)
        await self.facade_db.commit()

        self.redis_db.delete("rooms:*")

        self.logger.debug("Rooms are loaded")

    async def __load_teachers(self):
        teachers = [
            TeacherLoading.model_validate_redis(self.redis_db.hget(name=key.decode("utf-8"), key="teacher"))
            for key in self.redis_db.keys("teachers:*")
        ]

        await self.facade_db.bulk_insert_teacher(teachers)
        await self.facade_db.commit()

        self.redis_db.delete("teachers:*")

        self.logger.debug("Teachers are loaded")

    async def __load_lessons(self):
        lessons = [
            LessonLoading.model_validate_redis(self.redis_db.hget(name=key.decode("utf-8"), key="lesson"))
            for key in self.redis_db.keys("lessons:*")
        ]

        await self.facade_db.bulk_insert_lesson(lessons)
        await self.facade_db.commit()

        self.redis_db.delete("lessons:*")

        self.logger.debug("Lessons are loaded")