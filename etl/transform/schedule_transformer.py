from re import S
from etl.schemas.academic import AcademicLoading
from etl.schemas.corps import CorpsLoading
from etl.schemas.lesson import LessonExtracting, LessonLoading
from etl.schemas.room import RoomLoading
from etl.schemas.teacher import TeacherLoading
from etl.transform.base_transformer import BaseTransformer
from utils.asyncio.set import Set


class ScheduleTransformer(BaseTransformer):
    # __academics = Set()
    # __corps = Set()
    # __rooms = Set()
    # __teachers = Set()
    # __lessons = Set()

    def __init__(
            self,
            redis_host: str,
            redis_port: str,
            db: int,
            single_connection_client: bool = True,
            is_logged: bool = True
    ):
        super().__init__(redis_host, redis_port, db, single_connection_client, is_logged)

    async def transform(self):
        self.logger.info("Start transforming schedule")

        await self.__transform_corps()
        await self.__transform_rooms()
        await self.__transform_teachers()
        await self.__transform_lessons()

        self.logger.info("Schedule was transformed successfully")

    async def __transform_corps(self):
        self.logger.debug("Transform corps")

        corps = Set()

        for key in self.db.keys("corps:*"):
            corps: CorpsLoading = CorpsLoading.model_validate_redis(model=self.db.hget(name=key.decode("utf-8"), key="corp"))
            await corps.add(corps)

        self.db.delete("corps:*")

        async for corp in corps:
            self.db.hset(name=f"corps:{hash(corp)}", key="corp", value=corp.model_dump_redis())

    async def __transform_rooms(self):
        self.logger.debug("Transform rooms")

        rooms = Set()

        for key in self.db.keys("rooms:*"):
            room: RoomLoading = RoomLoading.model_validate_redis(model=self.db.hget(name=key.decode("utf-8"), key="room"))
            await rooms.add(room)

        self.db.delete("rooms:*")
        
        async for room in rooms:
            self.db.hset(name=f"rooms:{hash(room)}", key="room", value=room.model_dump_redis())

    async def __transform_teachers(self):
        self.logger.debug("Transform teachers")

        teachers = Set()

        for key in self.db.keys("teachers:*"):
            teacher: TeacherLoading = TeacherLoading.model_validate_redis(model=self.db.hget(name=key.decode("utf-8"), key="teacher"))
            await teachers.add(teacher)

        self.db.delete("teachers:*")

        async for teacher in teachers:
            self.db.hset(name=f"teachers:{hash(teacher)}", key="teacher", value=teacher.model_dump_redis())

    async def __transform_lessons(self):
        self.logger.debug("Transform lessons")

        academics = Set()
        lessons_loading = Set()
        lessons_extracting = {}

        for key in self.db.keys("lessons:*"):
            lesson: LessonExtracting = LessonExtracting.model_validate_redis(model=self.db.hget(name=key.decode("utf-8"), key="lesson"))
            await academics.add(AcademicLoading(name=lesson.academic))
            
            if lesson not in lessons_loading:
                await lessons_loading.add(hash(lesson))
            else:
                l: LessonLoading = lessons_extracting.get(hash(lesson))
                if l is not None:
                    l.groups.append(lesson.group)
                    l.rooms.append(lesson.room)
                    l.teachers.append(lesson.teacher)

        self.db.delete("lessons:*")

        async for academic in academics:
            self.db.hset(name=f"academics:{hash(academic)}", key="academic", value=academic.model_dump_redis())

        for lesson in lessons_extracting:
            self.db.hset(name=f"lessons:{hash(lesson)}", key="lesson", value=lesson.model_dump_redis())