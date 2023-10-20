from typing import Dict

from fastapi import HTTPException, Response
from pydantic import UUID4

from backend.api.database.models.teacher_translate import TeacherTranslateModel
from backend.api.schemas.lesson import (
    LessonCreateSchema,
    LessonOutputSchema,
    LessonsByGroupSchema,
    LessonsByTeacherSchema,
    LessonSchema,
)
from backend.api.schemas.lesson_translate import LessonTranslateCreateSchema
from backend.api.schemas.teacher import TeacherSchema
from backend.api.schemas.teacher_translate import TeacherTranslateSchema
from backend.api.services.base_servise import BaseService


class LessonService(BaseService):
    # TODO fix set_dependencies
    async def create(self, schemas: LessonCreateSchema) -> LessonOutputSchema:
        lesson = await self.facade.get_unique_lesson(schemas)
        if lesson is not None:
            raise HTTPException(409, detail="Занятие уже существует")

        lesson = await self.facade.get_lesson_lesson(schemas)
        if lesson is None:
            lesson = await self.facade.create_lesson(schemas)
            await self.facade.create_lesson_translate(
                LessonTranslateCreateSchema(
                    type=schemas.type,
                    name=schemas.name,
                    subgroup=schemas.subgroup,
                    lang=schemas.lang,
                    lesson_guid=lesson.guid,
                )
            )
        else:
            lesson = await self.facade.set_dependencies(
                lesson, group=schemas.group, room=schemas.room, teacher_name=schemas.teacher_name
            )
            await self.facade.commit()
        await self.facade.refresh(lesson)

        trans = lesson.trans
        for tr in trans:
            if tr.lang != schemas.lang:
                lesson.trans.remove(tr)

        await self.facade.commit()

        return LessonOutputSchema(**LessonSchema.model_validate(lesson).model_dump())

    async def get(self, guid: UUID4, lang: str) -> LessonOutputSchema:
        lesson = await self.facade.get_by_id_lesson(guid)
        if lesson is None:
            raise HTTPException(404, "Занятие не найдено")
        trans = lesson.trans
        for tr in trans:
            if tr.lang != lang:
                lesson.trans.remove(tr)
        return LessonOutputSchema(**LessonSchema.model_validate(lesson).model_dump())

    async def get_guid(self, schemas: LessonCreateSchema) -> UUID4:
        lesson = await self.facade.get_id_lesson(schemas)
        if lesson is None:
            raise HTTPException(404, "Занятие не найдено")
        return lesson

    async def get_by_group(self, group: str, lang: str) -> Dict:
        lessons = await self.facade.get_by_group_lesson(group, lang)

        if not lessons:
            raise HTTPException(404, "Занятий не найдено")

        lessons_schemes = []
        for lesson in lessons:
            trans = await self.facade.get_trans_lesson(lesson, lang)
            if trans is None:
                raise HTTPException(404, "Занятие не найдено")

            lessons_schemes.append(
                LessonOutputSchema(
                    **LessonSchema(
                        guid=lesson.guid,
                        time_start=lesson.time_start,
                        time_end=lesson.time_end,
                        date_start=lesson.date_start,
                        date_end=lesson.date_end,
                        dot=lesson.dot,
                        weeks=lesson.weeks,
                        day=lesson.day,
                        trans=trans,
                        rooms=await self.facade.get_rooms_lesson(lesson),
                        groups=await self.facade.get_groups_lesson(lesson),
                        teachers=[
                            TeacherSchema(
                                guid=t[0].guid,
                                url=t[0].url,
                                alt_url=t[0].alt_url,
                                trans=[
                                    TeacherTranslateSchema(
                                        guid=t[1].guid, name=t[1].name, fullname=t[1].fullname, lang=t[1].lang
                                    )
                                ]
                                if t[1]
                                else [],
                            )
                            for t in await self.facade.get_teachers_lesson(lesson, "ru" if lang == "ru" else "en")
                        ],
                    ).model_dump()
                )
            )

        return LessonsByGroupSchema(lessons=lessons_schemes, group=group, lang=lang).dict()

    async def get_by_teacher(self, teacher: str, lang: str) -> Dict:
        lessons = await self.facade.get_by_teacher_lesson(teacher, lang)

        if not lessons:
            raise HTTPException(404, "Занятий не найдено")

        lessons_schemes = []
        for lesson in lessons:
            trans = await self.facade.get_trans_lesson(lesson, lang)
            if trans is None:
                raise HTTPException(404, "Занятие не найдено")

            lessons_schemes.append(
                LessonOutputSchema(
                    **LessonSchema(
                        guid=lesson.guid,
                        time_start=lesson.time_start,
                        time_end=lesson.time_end,
                        date_start=lesson.date_start,
                        date_end=lesson.date_end,
                        dot=lesson.dot,
                        weeks=lesson.weeks,
                        day=lesson.day,
                        trans=trans,
                        rooms=await self.facade.get_rooms_lesson(lesson),
                        groups=await self.facade.get_groups_lesson(lesson),
                        teachers=[
                            TeacherSchema(
                                guid=t[0].guid,
                                url=t[0].url,
                                alt_url=t[0].alt_url,
                                trans=[
                                    TeacherTranslateSchema(
                                        guid=t[1].guid, name=t[1].name, fullname=t[1].fullname, lang=t[1].lang
                                    )
                                ]
                                if t[1]
                                else [],
                            )
                            for t in await self.facade.get_teachers_lesson(lesson, "ru" if lang == "ru" else "en")
                        ],
                    ).model_dump()
                )
            )

        t = await self.facade.get_by_name_teacher(teacher)
        t_trans = await self.facade.get_trans_teacher(t, lang="ru")
        name_ru = t_trans.name
        fullname_ru = t_trans.fullname
        if lang != "ru":
            t_trans = await self.facade.get_trans_teacher(t, lang="en")
        return LessonsByTeacherSchema(
            lessons=lessons_schemes,
            name=t_trans.name,
            fullname=t_trans.fullname,
            name_ru=name_ru,
            fullname_ru=fullname_ru,
            url=t.url,
            alt_url=t.alt_url,
            lang=lang,
        ).dict()

    async def update(self, guid: UUID4, schemas: LessonCreateSchema) -> LessonOutputSchema:
        lesson = await self.facade.update_lesson(guid, schemas)
        if lesson is None:
            raise HTTPException(404, "Занятие не найдено")

        trans = lesson.trans
        for tr in trans:
            if tr.lang != schemas.lang:
                lesson.trans.remove(tr)

        await self.facade.commit()
        return LessonOutputSchema(**LessonSchema.model_validate(lesson).model_dump())

    async def update_translate(self, schemas: LessonCreateSchema, guid: UUID4) -> LessonOutputSchema:
        lesson = await self.facade.update_translate_lesson(schemas, guid)
        if lesson is None:
            raise HTTPException(404, "Занятие не найдено")

        trans = lesson.trans
        for tr in trans:
            if tr.lang != schemas.lang:
                lesson.trans.remove(tr)

        await self.facade.commit()
        return LessonOutputSchema(**LessonSchema.model_validate(lesson).model_dump())

    async def delete(self, guid: UUID4) -> Response:
        await self.facade.delete_lesson(guid)
        await self.facade.commit()

        return Response(status_code=204)
