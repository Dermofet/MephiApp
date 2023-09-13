import sqlalchemy
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

        try:
            await self.__load_academics()
            await self.__load_corps()
            await self.__load_rooms()
            await self.__load_teachers()
            await self.__load_lessons()
            await self.facade_db.commit()
        except Exception as e:
            self.logger.error(f"Can't loading data: {e}")
            await self.facade_db.rollback()

        self.logger.info("Schedule loaded successfully")

    async def __load_academics(self):
        academics = [
            AcademicLoading.model_validate_redis(self.redis_db.hget(name=key.decode("utf-8"), key="academic"))
            for key in self.redis_db.scan_iter("academics:*")
        ]

        await self.facade_db.bulk_insert_academic(academics)

        for key in self.redis_db.scan_iter("academics:*"):
            self.redis_db.delete(key)

        self.logger.debug("Academics are loaded")

    async def __load_corps(self):
        corps = [
            CorpsLoading.model_validate_redis(self.redis_db.hget(name=key.decode("utf-8"), key="corp"))
            for key in self.redis_db.scan_iter("corps:*")
        ]

        await self.facade_db.bulk_insert_corps(corps)

        for key in self.redis_db.scan_iter("corps:*"):
            self.redis_db.delete(key)

        self.logger.debug("Corps are loaded")

    async def __load_rooms(self):
        rooms = [
            RoomLoading.model_validate_redis(self.redis_db.hget(name=key.decode("utf-8"), key="room"))
            for key in self.redis_db.keys("rooms:*")
        ]

        await self.facade_db.bulk_insert_room(rooms)

        for key in self.redis_db.scan_iter("rooms:*"):
            self.redis_db.delete(key)

        self.logger.debug("Rooms are loaded")

    async def __load_teachers(self):
        teachers = [
            TeacherLoading.model_validate_redis(self.redis_db.hget(name=key.decode("utf-8"), key="teacher"))
            for key in self.redis_db.scan_iter("teachers:*")
        ]

        await self.facade_db.bulk_insert_teacher(teachers)

        for key in self.redis_db.scan_iter("teachers:*"):
            self.redis_db.delete(key)

        self.logger.debug("Teachers are loaded")

    async def __load_lessons(self):
        lessons = [
            LessonLoading.model_validate_redis(self.redis_db.hget(name=key.decode("utf-8"), key="lesson"))
            for key in self.redis_db.scan_iter("lessons:*")
        ]

        await self.facade_db.bulk_insert_lesson(lessons)

        for key in self.redis_db.scan_iter("lessons:*"):
            self.redis_db.delete(key)

        self.logger.debug("Lessons are loaded")