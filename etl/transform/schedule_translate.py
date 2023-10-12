from typing import List
from backend.api.database.models.lesson_translate import LessonTranslateModel
from backend.api.database.models.teacher_translate import TeacherTranslateModel
from etl.loaders.base_loader import BaseLoader

from etl.translate.translator import YandexTranslator

class ScheduleTranslate(BaseLoader):
    max_chars_per_request = 10000
    def __init__(
            self, 
            langs: List[str], 
            iam_token: str, 
            folder_id: str,
            redis: str,
            postgres_dsn: str,
            single_connection_client=True,
            is_logged=True,
            debug=False
        ):
        super().__init__(
            redis=redis,
            postgres_dsn=postgres_dsn,
            single_connection_client=single_connection_client,
            is_logged=is_logged,
            debug=debug
        )
        self.translator = YandexTranslator(
            iam_token=iam_token,
            folder_id=folder_id
        )
        self.langs = langs

    async def translate(self):
        try:
            await self.translate_lessons()
            await self.translate_teachers()
            await self.facade_db.commit()
            self.logger.info("Schedule were translated successfully")
        except Exception:
            self.logger.error("Can't translate schedule")
            await self.facade_db.rollback()

    async def translate_lessons(self):
        self.logger.info("Translate lessons...")

        limit = 1000
        offset = 0

        while True:
            lessons = await self.facade_db.get_all_lesson(limit=limit, offset=offset)
            if len(lessons) == 0:
                break

            for lang in self.langs:
                self.logger.debug(f"Translate lessons for {lang}")
                translated_lessons = await self.translate_lessons_by_lang(lang, lessons)
                await self.update_lessons_translations(lessons, translated_lessons, lang)

            offset += limit

    async def translate_lessons_by_lang(self, lang, lessons):
        translated_lessons = []
        text = []
        total_len = 0
        for lesson in lessons:
            trans = await self.facade_db.get_trans_lesson(lesson, "ru")

            subgroup_len = len(trans.subgroup) if trans.subgroup is not None else 0
            type_len = len(trans.type) if trans.type is not None else 0
            if total_len + len(trans.name) + subgroup_len + type_len < self.max_chars_per_request:
                text.extend((trans.name, trans.subgroup, trans.type))
                total_len += len(trans.name) + subgroup_len + type_len
            else:
                tr = self.translator.translate(source="ru", target=lang, text=text)
                translated_lessons.extend(tr)

                text = [trans.name, trans.subgroup, trans.type]
                total_len = len(trans.name) + subgroup_len + type_len

        tr = self.translator.translate(source="ru", target=lang, text=text)
        translated_lessons.extend(tr)

        return translated_lessons

    async def update_lessons_translations(self, lessons, translated_lessons, lang):
        chunk_size = 3
        chunk_flush = 1000
        i = 1
        for lesson, chunk in zip(lessons, zip(*[iter(translated_lessons)] * chunk_size)):
            if i % chunk_flush == 0:
                self.logger.debug(f"Insert {i} lessons")
                await self.facade_db.flush()
            
            lesson.trans.add(
                LessonTranslateModel(
                    name=chunk[0],
                    subgroup=chunk[1],
                    type=chunk[2],
                    lang=lang,
                )
            )
            i += 1

        self.logger.debug(f"Insert {i} lessons")
        await self.facade_db.flush()

    async def translate_lesson_types(self):
        types = {}
        for lang in self.langs:
            tr = self.translator.translate("ru", lang, ["лекция", "практика", "лабораторная работа", "аудиторная работа"])
            types[lang] = {
                "лекция": tr[0],
                "практика": tr[1],
                "лабораторная работа": tr[2],
                "аудиторная работа": tr[3],
            }
        return types

    async def translate_teachers(self):
        self.logger.info("Translate teachers...")

        teachers = await self.facade_db.get_all_full_teacher("ru")
        if teachers is None:
            return

        self.logger.debug("Translate teachers for en")

        total_len = 0
        text = []
        translated_teachers = []
        for teacher in teachers:
            trans = await self.facade_db.get_trans_teacher(teacher, "ru")
            if total_len + len(trans.fullname) < self.max_chars_per_request:
                text.append(trans.fullname)
                total_len += len(trans.fullname)
            else:
                translated_teachers.extend(self.translator.translate(source="ru", target="en", text=text))
                text = [trans.fullname]
                total_len = len(trans.fullname)

        await self.update_teachers_translations(teachers, translated_teachers)

    async def update_teachers_translations(self, teachers, translated_teachers):
        chunk_flush = 1000
        i = 1
        for teacher, fullname in zip(teachers, translated_teachers):
            if i % chunk_flush == 0:
                self.logger.debug(f"Insert {i} teachers")
                await self.facade_db.flush()

            name_parts = fullname.split()
            teacher.trans.add(
                TeacherTranslateModel(
                    name=f"{name_parts[0]} {'.'.join([i[0] for i in name_parts[1:]])}.",
                    fullname=fullname,
                    lang="en"
                )
            )
            i += 1

        self.logger.debug(f"Insert {i} teachers")
        await self.facade_db.flush()
