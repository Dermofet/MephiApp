import asyncio
from typing import List

from aiohttp import ClientSession

from backend.database.models.lesson import LessonModel
from backend.database.models.lesson_translate import LessonTranslateModel


async def translate(session: ClientSession, text: str, src_lang: str, dest_lang: str) -> str:
    async with session.get(
            f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={src_lang}&tl={dest_lang}&dt=t&q={text}") as resp:
        result = await resp.json()
        return result[0][0][0]


async def translate_field(session: ClientSession, field: str, src_lang: str, dest_lang: str) -> str:
    if field is None:
        return ""
    return await translate(session, field, src_lang, dest_lang)


async def translate_lesson(db, session, lesson: LessonModel, langs: List[str], preset_values) -> LessonModel:
    trans = lesson.trans[0]
    for lang in langs:
        name = await translate_field(session, trans.name, 'ru', lang)
        type_ = preset_values[lang]["type"][trans.type] if trans.type is not None else ""
        subgroup = await translate_field(session, trans.subgroup, 'ru', lang)

        new_trans = LessonTranslateModel(
            name=name,
            type=type_ if type_ != "" else None,
            subgroup=subgroup if subgroup != "" else None,
            lang=lang
        )
        db.add(new_trans)
        lesson.trans.append(new_trans)
    return lesson


async def translate_lesson_types(session: ClientSession, langs: List[str]):
    preset_values = {}
    for lang in langs:
        if lang == "ru":
            continue
        practice_type = await translate_field(session, "Практика", src_lang="ru", dest_lang=lang)
        lecture_type = await translate_field(session, "Лекция", src_lang="ru", dest_lang=lang)
        lab_type = await translate_field(session, "Лабораторная работа", src_lang="ru", dest_lang=lang)
        aud_type = await translate_field(session, "Аудиторная работа", src_lang="ru", dest_lang=lang)
        preset_values[lang] = {
                "type": {
                    "Пр": practice_type,
                    "Лек": lecture_type,
                    "Лаб": lab_type,
                    "Ауд": aud_type
                }
            }
    return preset_values


async def translate_lessons(db, lessons: List[LessonModel], langs: List[str]):
    limit = 1000
    tasks = []
    i = 1
    async with ClientSession(trust_env=True) as session:
        preset_values = await translate_lesson_types(session, langs)
        for lesson in lessons:
            tasks.append(asyncio.create_task(translate_lesson(db, session, lesson, langs, preset_values)))
            if len(tasks) == limit:
                print(i)
                await asyncio.gather(*tasks)
                tasks.clear()
                await asyncio.sleep(3)
            i += 1
        if tasks:
            await asyncio.gather(*tasks)

