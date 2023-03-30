import asyncio
from typing import List

from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.teacher import TeacherModel
from backend.database.models.teacher_translate import TeacherTranslateModel


async def translate(session: ClientSession, text: str, src_lang: str, dest_lang: str) -> str:
    async with session.get(
            f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={src_lang}&tl={dest_lang}&dt=t&q={text}") as resp:
        result = await resp.json()
        return result[0][0][0]


async def translate_field(session: ClientSession, field: str, src_lang: str, dest_lang: str) -> str:
    if field is None:
        return ""
    return await translate(session, field, src_lang, dest_lang)


async def translate_teacher(db, session, teacher: TeacherModel, langs: List[str]) -> TeacherModel:
    trans = teacher.trans[0]
    for lang in langs:
        fullname = await translate_field(session, trans.fullname, 'ru', lang)
        buf = fullname.split()
        if len(buf) == 2:
            name = buf[0] + " " + buf[1][0] + "."
        else:
            name = buf[0] + " " + buf[1][0] + "." + buf[2][0] + "."

        new_trans = TeacherTranslateModel(
            name=name,
            fullname=fullname,
            teacher_guid=teacher.guid,
            lang=lang
        )
        db.add(new_trans)
        teacher.trans.append(new_trans)
    return teacher


async def translate_teachers(db, teachers: List[TeacherModel], langs: List[str]):
    limit = 1000
    tasks = []
    i = 1
    async with ClientSession(trust_env=True) as session:
        for teacher in teachers:
            tasks.append(asyncio.create_task(translate_teacher(db, session, teacher, langs)))
            if len(tasks) == limit:
                print(i)
                await asyncio.gather(*tasks)
                tasks.clear()
                await asyncio.sleep(3)
            i += 1
        if tasks:
            await asyncio.gather(*tasks)

