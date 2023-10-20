from typing import List, Union

from etl.loaders.base_loader import BaseLoader
from etl.schemas.lesson import LessonTranslateLoading
from etl.schemas.teacher import TeacherTranslateLoading
from etl.translate.translator import YandexTranslator


class ScheduleTranslate(BaseLoader):
    max_chars_per_request = 10000
    translator: YandexTranslator
    langs: List[str]
    index = 0

    def __init__(
        self,
        langs: List[str],
        iam_token: str,
        folder_id: str,
        redis: str,
        postgres_dsn: str,
        single_connection_client=True,
        is_logged=True,
        debug=False,
    ):
        super().__init__(
            redis=redis,
            postgres_dsn=postgres_dsn,
            single_connection_client=single_connection_client,
            is_logged=is_logged,
            debug=debug,
        )
        self.translator = YandexTranslator(iam_token=iam_token, folder_id=folder_id)
        self.langs = langs

    async def translate(self):
        try:
            await self.translate_lessons()
            await self.translate_teachers()
            self.logger.info("Schedule were translated successfully")
        except Exception as e:
            self.logger.error("Can't translate schedule")
            raise e

    async def translate_lessons(self):
        self.logger.info("Translate lessons...")

        limit = 1000
        offset = 0

        while True:
            await self.session.close()
            self.init_facade()

            trans = await self.facade_db.get_all_trans_lesson(limit=limit, offset=offset, lang="ru")
            if len(trans) == 0:
                break

            for lang in self.langs:
                self.logger.debug(f"Translate lessons for {lang}")
                translated_lessons = await self.translate_lessons_by_lang(lang, trans)
                tr = self.create_lessons_translations(trans, translated_lessons, lang)
                self.set_to_redis(tr, "lesson_translate", "trans")

            offset += limit

    async def translate_lessons_by_lang(self, lang, trans):
        translated_lessons = []
        text = []
        total_len = 0

        for t in trans:
            subgroup_len = len(t.subgroup) if t.subgroup is not None else 0
            type_len = len(t.type) if t.type is not None else 0
            name_len = len(t.name)

            if total_len + name_len + subgroup_len + type_len < self.max_chars_per_request:
                text.extend((t.name, t.subgroup, t.type))
                total_len += name_len + subgroup_len + type_len
            else:
                tr = self.translator.translate(source="ru", target=lang, text=text)
                translated_lessons.extend(tr)

                text = [t.name, t.subgroup, t.type]
                total_len = name_len + subgroup_len + type_len

        tr = self.translator.translate(source="ru", target=lang, text=text)
        translated_lessons.extend(tr)

        return translated_lessons

    def create_lessons_translations(self, trans, translated_lessons, lang):
        chunk_size = 3
        return [
            LessonTranslateLoading(
                lesson_guid=str(tr.lesson_guid),
                name=chunk[0],
                subgroup=chunk[1],
                type=chunk[2],
                lang=lang,
            )
            for tr, chunk in zip(trans, zip(*[iter(translated_lessons)] * chunk_size))
        ]

    async def translate_lesson_types(self):
        types = {}
        for lang in self.langs:
            tr = self.translator.translate(
                "ru", lang, ["лекция", "практика", "лабораторная работа", "аудиторная работа"]
            )
            types[lang] = {
                "лекция": tr[0],
                "практика": tr[1],
                "лабораторная работа": tr[2],
                "аудиторная работа": tr[3],
            }
        return types

    async def translate_teachers(self):
        self.logger.info("Translate teachers...")

        await self.session.close()
        self.init_facade()

        trans = await self.facade_db.get_all_trans_teacher(lang="ru")
        if trans is None:
            return

        self.logger.debug("Translate teachers for en")

        total_len = 0
        text = []
        translated_teachers = []
        for t in trans:
            if total_len + len(t.fullname) < self.max_chars_per_request:
                text.append(t.fullname)
                total_len += len(t.fullname)
            else:
                translated_teachers.extend(self.translator.translate(source="ru", target="en", text=text))
                text = [t.fullname]
                total_len = len(t.fullname)

        translated_teachers.extend(self.translator.translate(source="ru", target="en", text=text))

        tr = self.create_teachers_translations(trans, translated_teachers)
        self.set_to_redis(tr, "teacher_translate", "trans")

    def create_teachers_translations(self, trans, translated_teachers):
        res = []
        for t, fullname in zip(trans, translated_teachers):
            name_parts = fullname.split()
            res.append(
                TeacherTranslateLoading(
                    teacher_guid=str(t.teacher_guid),
                    name=f"{name_parts[0]} {'.'.join([i[0] for i in name_parts[1:]])}.",
                    fullname=fullname,
                    lang="en",
                )
            )
        return res

    def set_to_redis(self, data: List[Union[LessonTranslateLoading, TeacherTranslateLoading]], name, key):
        for item in data:
            self.redis_db.hset(name=f"{name}:{self.index}", key=key, value=item.model_dump_redis())
            self.index += 1
