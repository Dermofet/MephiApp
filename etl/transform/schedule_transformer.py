from typing import List

from etl.schemas.academic import AcademicLoading
from etl.schemas.corps import CorpsLoading
from etl.schemas.group import GroupLoading
from etl.schemas.lesson import LessonExtracting, LessonLoading, LessonTranslateLoading, RoomLessonExtracting
from etl.schemas.room import RoomLoading
from etl.schemas.teacher import TeacherFullnameLoading, TeacherLoading, TeacherTranslateLoading
from etl.transform.base_transformer import BaseTransformer
from utils.asyncio.set import Set


class ScheduleTransformer(BaseTransformer):
    langs: List[str]

    def __init__(
        self,
        redis: str,
        langs: List[str],
        single_connection_client: bool = True,
        is_logged: bool = True,
    ):
        super().__init__(redis, single_connection_client, is_logged)

        self.langs = langs

    async def transform(self):
        self.logger.info("Start transforming schedule")

        await self.__transform_corps()
        await self.__transform_rooms()
        await self.__transform_teachers()
        await self.__transform_lessons()

        self.logger.info("Schedule was transformed successfully")

    async def __transform_corps(self):
        self.logger.debug("Transform corps")
        await self.__transform_items("corps:*", "corp", CorpsLoading)

    async def __transform_rooms(self):
        self.logger.debug("Transform rooms")
        await self.__transform_items("rooms:*", "room", RoomLoading)

    async def __transform_teachers(self):
        self.logger.debug("Transform teachers")
        await self.__transform_teacher_items()

    async def __transform_teacher_items(self):
        items_set = Set()

        for key in self.db.scan_iter("teachers:*"):
            item = TeacherFullnameLoading.model_validate_redis(
                model=self.db.hget(name=key.decode("utf-8"), key="teacher")
            )
            await items_set.add(item)

        for key in self.db.scan_iter("teachers:*"):
            self.db.delete(key)

        async for item in items_set:
            self.db.hset(
                name=f"teachers:{hash(item)}", 
                key="teacher", 
                value=TeacherLoading(
                    url=item.url,
                    alt_url=item.alt_url,
                    trans=[
                        TeacherTranslateLoading(
                            teacher_guid=None,
                            lang=item.lang,
                            name=item.name,
                            fullname=item.fullname,
                        )
                    ],
                ).model_dump_redis()
            )

    async def __transform_items(self, key_pattern, key_field, item_type):
        items_set = Set()

        for key in self.db.scan_iter(key_pattern):
            item = item_type.model_validate_redis(
                model=self.db.hget(name=key.decode("utf-8"), key=key_field)
            )
            await items_set.add(item)

        for key in self.db.scan_iter(key_pattern):
            self.db.delete(key)

        async for item in items_set:
            self.db.hset(
                name=f"{key_field}s:{hash(item)}", key=key_field, value=item.model_dump_redis()
            )

    async def __transform_lessons(self):
        self.logger.debug("Transform lessons")

        academics = Set()
        groups = Set()
        lessons_loading = {}

        await self.__transform_lesson_items("lessons:*", "lesson", LessonExtracting, academics, groups, lessons_loading)
        await self.__transform_lesson_items("room_lessons:*", "room_lesson", RoomLessonExtracting, academics, groups, lessons_loading)

        await self.__transform_academic_items(academics)
        await self.__transform_group_items(groups)
        await self.__transform_lesson_items_dict(lessons_loading)

    async def __transform_lesson_items(self, key_pattern, key_field, item_type, academics, groups, lessons_loading):
        for key in self.db.scan_iter(key_pattern):
            lesson = item_type.model_validate_redis(
                model=self.db.hget(name=key.decode("utf-8"), key=key_field)
            )

            if item_type == LessonExtracting:
                await academics.add(AcademicLoading(name=lesson.academic))
                await groups.add(
                    GroupLoading(
                        name=lesson.group,
                        course=int(lesson.course),
                        academic=lesson.academic,
                    )
                )

            lesson_loading = LessonLoading(
                time_start=lesson.time_start,
                time_end=lesson.time_end,
                dot=lesson.dot,
                day=lesson.day,
                date_start=lesson.date_start,
                date_end=lesson.date_end,
                weeks=lesson.weeks,
                groups=set(),
                teachers=set(),
                rooms=set(),
                trans=[
                    LessonTranslateLoading(
                        lesson_guid=None,
                        type=lesson.type,
                        subgroup=lesson.subgroup,
                        name=lesson.name,
                        lang=lesson.lang,
                    )
                ],
            )

            lesson_loading.groups.add(lesson.group)
            if lesson.room is not None:
                lesson_loading.rooms.add(lesson.room)
            for teacher in lesson.teachers:
                lesson_loading.teachers.add(teacher)

            if lessons_loading.get(hash(lesson_loading)) is not None:
                lessons_loading[hash(lesson_loading)].groups = lessons_loading[
                    hash(lesson_loading)
                ].groups.union(lesson_loading.groups)
                lessons_loading[hash(lesson_loading)].teachers = lessons_loading[
                    hash(lesson_loading)
                ].teachers.union(lesson_loading.teachers)
            else:
                lessons_loading[hash(lesson_loading)] = lesson_loading

        for key in self.db.scan_iter(key_pattern):
            self.db.delete(key)

    async def __transform_academic_items(self, academics):
        async for academic in academics:
            self.db.hset(
                name=f"academics:{hash(academic)}",
                key="academic",
                value=academic.model_dump_redis(),
            )

    async def __transform_group_items(self, groups):
        async for group in groups:
            self.db.hset(
                name=f"groups:{hash(group)}", key="group", value=group.model_dump_redis()
            )

    async def __transform_lesson_items_dict(self, lessons_loading):
        for lesson in lessons_loading.values():
            self.db.hset(
                name=f"lessons:{hash(lesson)}",
                key="lesson",
                value=lesson.model_dump_redis(),
            )