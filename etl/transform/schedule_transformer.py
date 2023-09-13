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

        corps_set = Set()

        for key in self.db.scan_iter("corps:*"):
            corps: CorpsLoading = CorpsLoading.model_validate_redis(self.db.hget(name=key.decode("utf-8"), key="corp"))

            await corps_set.add(corps)

        for key in self.db.scan_iter("corps:*"):
            self.db.delete(key)

        async for corp in corps_set:
            self.db.hset(name=f"corps:{hash(corp)}", key="corp", value=corp.model_dump_redis())

    async def __transform_rooms(self):
        self.logger.debug("Transform rooms")

        rooms_set = Set()

        for key in self.db.scan_iter("rooms:*"):
            room: RoomLoading = RoomLoading.model_validate_redis(model=self.db.hget(name=key.decode("utf-8"), key="room"))
            await rooms_set.add(room)

        for key in self.db.scan_iter("rooms:*"):
            self.db.delete(key)
        
        async for room in rooms_set:
            self.db.hset(name=f"rooms:{hash(room)}", key="room", value=room.model_dump_redis())

    async def __transform_teachers(self):
        self.logger.debug("Transform teachers")

        teachers_set = Set()

        for key in self.db.scan_iter("teachers:*"):
            teacher: TeacherLoading = TeacherLoading.model_validate_redis(model=self.db.hget(name=key.decode("utf-8"), key="teacher"))
            await teachers_set.add(teacher)

        for key in self.db.scan_iter("teachers:*"):
            self.db.delete(key)

        async for teacher in teachers_set:
            self.db.hset(name=f"teachers:{hash(teacher)}", key="teacher", value=teacher.model_dump_redis())

    async def __transform_lessons(self):
        self.logger.debug("Transform lessons")

        academics = Set()
        lessons_loading = {}
        lessons_extracting = Set()

        for key in self.db.scan_iter("lessons:*"):
            lesson: LessonExtracting = LessonExtracting.model_validate_redis(model=self.db.hget(name=key.decode("utf-8"), key="lesson"))
            await academics.add(AcademicLoading(name=lesson.academic))

            if lesson not in lessons_extracting:
                await lessons_extracting.add(hash(lesson))
                lessons_loading[hash(lesson)] = LessonLoading(
                    time_start=lesson.time_start,
                    time_end=lesson.time_end,
                    dot=lesson.dot,
                    room=lesson.room,
                    day=lesson.day,
                    date_start=lesson.date_start,
                    date_end=lesson.date_end,
                    weeks=lesson.weeks,
                    course=lesson.course,
                    lang=lesson.lang,
                    type=lesson.type,
                    subgroup=lesson.subgroup,
                    name=lesson.name,
                    groups=set(),
                    teachers=set(),
                    rooms=set(),
                )
                
            lessons_loading[hash(lesson)].groups.add(lesson.group)
            if lesson.room is not None:
                lessons_loading[hash(lesson)].rooms.add(lesson.room)
            for teacher in lesson.teachers:
                lessons_loading[hash(lesson)].teachers.add(teacher)

        for key in self.db.scan_iter("lessons:*"):
            self.db.delete(key)

        async for academic in academics:
            self.db.hset(name=f"academics:{hash(academic)}", key="academic", value=academic.model_dump_redis())

        for lesson in lessons_loading.values():
            self.db.hset(name=f"lessons:{hash(lesson)}", key="lesson", value=lesson.model_dump_redis())