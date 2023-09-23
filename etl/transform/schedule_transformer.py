import time
from typing import List

# from googletrans import Translator
from deep_translator import GoogleTranslator, MyMemoryTranslator
from etl.schemas.academic import AcademicLoading
from etl.schemas.corps import CorpsLoading
from etl.schemas.group import GroupLoading
from etl.schemas.lesson import LessonExtracting, LessonLoading, LessonTranslateLoading
from etl.schemas.room import RoomLoading
from etl.schemas.teacher import TeacherFullnameLoading, TeacherLoading, TeacherTranslateLoading
from etl.transform.base_transformer import BaseTransformer
from utils.asyncio.set import Set


class ScheduleTransformer(BaseTransformer):
    langs: List[str]

    def __init__(
            self,
            redis_host: str,
            redis_port: str,
            db: int,
            langs: List[str],
            single_connection_client: bool = True,
            is_logged: bool = True
    ):
        super().__init__(redis_host, redis_port, db, single_connection_client, is_logged)

        self.langs = langs

    async def transform(self):
        self.logger.info("Start transforming schedule")

        await self.__transform_corps()
        await self.__transform_rooms()
        await self.__transform_teachers()
        await self.__transform_lessons()
        # await self.__transform_translate_teachers()
        # await self.__transform_translate_lessons()

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
            teacher: TeacherFullnameLoading = TeacherFullnameLoading.model_validate_redis(model=self.db.hget(name=key.decode("utf-8"), key="teacher"))
            await teachers_set.add(
                TeacherLoading(
                    url=teacher.url,
                    alt_url=teacher.alt_url,
                    trans=[
                        TeacherTranslateLoading(
                            name=teacher.name,
                            fullname=teacher.fullname,
                            lang=teacher.lang
                        )
                    ]
                )
            )

        for key in self.db.scan_iter("teachers:*"):
            self.db.delete(key)

        async for teacher in teachers_set:
            self.db.hset(name=f"teachers:{hash(teacher)}", key="teacher", value=teacher.model_dump_redis())

    async def __transform_lessons(self):
        self.logger.debug("Transform lessons")

        academics = Set()
        groups = Set()
        lessons_loading = {}

        for key in self.db.scan_iter("lessons:*"):
            lesson: LessonExtracting = LessonExtracting.model_validate_redis(model=self.db.hget(name=key.decode("utf-8"), key="lesson"))
            await academics.add(AcademicLoading(name=lesson.academic))
            await groups.add(
                GroupLoading(
                    name=lesson.group,
                    course=int(lesson.course),
                    academic=lesson.academic,
                )
            )

            lesson_loading=LessonLoading(
                time_start=lesson.time_start,
                time_end=lesson.time_end,
                dot=lesson.dot,
                room=lesson.room,
                day=lesson.day,
                date_start=lesson.date_start,
                date_end=lesson.date_end,
                weeks=lesson.weeks,
                course=lesson.course,
                groups=set(),
                teachers=set(),
                rooms=set(),
                trans=[
                    LessonTranslateLoading(
                        type=lesson.type,
                        subgroup=lesson.subgroup,
                        name=lesson.name,
                        lang=lesson.lang
                    )
                ]
            )
                
            lesson_loading.groups.add(lesson.group)
            if lesson.room is not None:
                lesson_loading.rooms.add(lesson.room)
            for teacher in lesson.teachers:
                lesson_loading.teachers.add(teacher)

            if lessons_loading.get(hash(lesson_loading)) is not None:
                lessons_loading[hash(lesson_loading)].groups = lessons_loading[hash(lesson_loading)].groups.union(lesson_loading.groups)
                lessons_loading[hash(lesson_loading)].teachers = lessons_loading[hash(lesson_loading)].teachers.union(lesson_loading.teachers)
            else:
                lessons_loading[hash(lesson_loading)] = lesson_loading

        for key in self.db.scan_iter("lessons:*"):
            self.db.delete(key)

        async for academic in academics:
            self.db.hset(name=f"academics:{hash(academic)}", key="academic", value=academic.model_dump_redis())

        async for group in groups:
            self.db.hset(name=f"groups:{hash(group)}", key="group", value=group.model_dump_redis())

        for lesson in lessons_loading.values():
            self.db.hset(name=f"lessons:{hash(lesson)}", key="lesson", value=lesson.model_dump_redis())

    async def __transform_translate_lessons(self):
        self.logger.debug("Transform translate lessons")

        translators = [GoogleTranslator(target=lang) for lang in self.langs]

        for key in self.db.scan_iter("lessons:*"):
            lesson: LessonLoading = LessonLoading.model_validate_redis(model=self.db.hget(name=key.decode("utf-8"), key="lesson"))
            for translator in translators:
                tr = translator.translate_batch([lesson.trans[0].type, lesson.trans[0].name, lesson.trans[0].subgroup])
                lesson.trans.append(
                    LessonTranslateLoading(
                        type=tr[0],
                        name=tr[1],
                        subgroup=tr[2],
                        lang=translator.target[:1],
                    )
                )
            self.db.hset(name=key, key="lesson", value=lesson.model_dump_redis())

    async def __transform_translate_teachers(self):
        self.logger.debug("Transform translate teachers")

        translator = GoogleTranslator('ru', 'en')

        teachers = []

        # Создайте список для хранения слов для перевода
        words_to_translate = []

        for key in self.db.scan_iter("teachers:*"):
            teacher_data = self.db.hget(name=key.decode("utf-8"), key="teacher")
            teacher = TeacherLoading.model_validate_redis(model=teacher_data)

            # Добавьте имена и полные имена в список для перевода
            words_to_translate.append(f'{teacher.trans[0].name} % {teacher.trans[0].fullname}')
            teachers.append(teacher)

        print(len(' | '.join(words_to_translate)))
        # Подготовьте список строк для перевода
        translations = []
        current_translation = ""

        for word in words_to_translate:
            if len(current_translation) + len(word) <= 4997:
                # Если текущая строка не превышает 500 символов, добавьте слово к ней
                current_translation += f"{word} | "
            else:
                # Если текущая строка превысила 500 символов, добавьте ее в список и начните новую
                translations.append(current_translation.rstrip(" | "))
                current_translation = f"{word} | "

        # Добавьте последнюю строку в список, если она не пуста
        if current_translation:
            translations.append(current_translation.rstrip(" | "))

        # Переведите список строк с помощью translate_batch()
        translated_parts = []
        for i, tr in enumerate(translations, start=1):
            print(i)
            translated_parts.append(translator.translate(tr))
            time.sleep(1)
        # Обновите переведенные данные в объектах TeacherLoading
        for teacher, translated_text in zip(teachers, translated_parts):
            # Разделите переведенный текст обратно на отдельные части
            translated_parts = translated_text.split(" | ")

            # Создайте объект TeacherTranslateLoading и добавьте его в список переводов
            translation = TeacherTranslateLoading(
                name=translated_parts[0],
                fullname=translated_parts[1],
                lang='en',
            )

            teacher.trans.append(translation)

            # Обновите данные о преподавателе в Redis
            self.db.hset(name=key, key="teacher", value=teacher.model_dump_redis())

