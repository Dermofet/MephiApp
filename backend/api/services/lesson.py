from typing import Dict

from fastapi import HTTPException, Response
from pydantic import UUID4

from backend.api.schemas.lesson import (
    LessonCreateSchema,
    LessonOutputSchema,
    LessonsByGroupSchema,
    LessonsByTeacherSchema,
    LessonSchema,
)
from backend.api.schemas.lesson_translate import LessonTranslateCreateSchema
from backend.api.services.base_servise import BaseService


class LessonService(BaseService):
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
                   lesson_guid=lesson.guid
               )
            )
        else:
            lesson = await self.facade.set_dependencies(
                lesson,
                group=schemas.group,
                room=schemas.room,
                teacher_name=schemas.teacher_name
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

        teacher_lang = "ru" if lang == "ru" else "en"
        for lesson in lessons:
            lesson.trans = [tr for tr in lesson.trans if tr.lang == lang]
            for teacher in lesson.teachers:
                teacher.trans = [tr for tr in teacher.trans if tr.lang == teacher_lang]

        lessons = [LessonOutputSchema(**LessonSchema.model_validate(lesson).model_dump()) for lesson in lessons]
        res = LessonsByGroupSchema(lessons=lessons, group=group, lang=lang)
        return res.model_dump()

    
    async def get_by_teacher(self, teacher: str, lang: str) -> Dict:
        lessons = await self.facade.get_by_teacher_lesson(teacher, lang)
        if not lessons:
            raise HTTPException(404, "Занятий не найдено")

        teacher_lang = "ru" if lang == "ru" else "en"
        teacher_model = await self.facade.get_by_name_teacher(teacher)
        teacher_model.trans = [tr for tr in teacher_model.trans if tr.lang == teacher_lang]

        for lesson in lessons:
            lesson.trans = [tr for tr in lesson.trans if tr.lang == lang]
            for teacher_ in lesson.teachers:
                teacher_.trans = [tr for tr in teacher_.trans if tr.lang == teacher_lang]

        lessons = [LessonOutputSchema(**LessonSchema.model_validate(lesson).model_dump()) for lesson in lessons]
        res = LessonsByTeacherSchema(lessons=lessons, teacher=teacher_model, lang=lang)
        return res.model_dump()

    
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
