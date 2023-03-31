from typing import List

from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.association_tables import *
from backend.database.models.lesson import LessonModel
from backend.repositories.group import GroupRepository
from backend.repositories.lesson import LessonRepository
from backend.repositories.lesson_translate import LessonTranslateRepository
from backend.repositories.room import RoomRepository
from backend.repositories.teacher import TeacherRepository
from backend.repositories.teacher_translate import TeacherTranslateRepository
from backend.schemas.lesson import (
    LessonCreateSchema,
    LessonOutputSchema,
    LessonsByGroupSchema,
    LessonsByTeacherSchema,
    LessonSchema,
)
from backend.schemas.lesson_translate import (
    LessonTranslateCreateSchema,
    LessonTranslateOutputSchema,
    LessonTranslateSchema,
)
from backend.schemas.teacher import TeacherSchema


class LessonService:
    @staticmethod
    async def create(db: AsyncSession, schemas: LessonCreateSchema) -> LessonOutputSchema:
        lesson = await LessonRepository.get_unique(db, schemas)
        if lesson is not None:
            raise HTTPException(409, detail="Занятие уже существует")
        else:
            lesson = await LessonRepository.get_lesson(db, schemas)
            if lesson is None:
                lesson = await LessonRepository.create(db, schemas)
                await LessonTranslateRepository.create(db,
                                                       LessonTranslateCreateSchema(
                                                           type=schemas.type,
                                                           name=schemas.name,
                                                           subgroup=schemas.subgroup,
                                                           lang=schemas.lang,
                                                           lesson_guid=lesson.guid))
            else:
                lesson = await LessonRepository.set_dependencies(db,
                                                                 lesson,
                                                                 group=schemas.group,
                                                                 room=schemas.room,
                                                                 teacher_name=schemas.teacher_name,
                                                                 lang=schemas.lang)
                await db.commit()
            await db.refresh(lesson)
        trans = lesson.trans
        for tr in trans:
            if tr.lang != schemas.lang:
                lesson.trans.remove(tr)
        return LessonOutputSchema(**LessonSchema.from_orm(lesson).dict())

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4, lang: str) -> LessonOutputSchema:
        lesson = await LessonRepository.get_by_id(db, guid)
        if lesson is None:
            raise HTTPException(404, "Занятие не найдено")
        trans = lesson.trans
        for tr in trans:
            if tr.lang != lang:
                lesson.trans.remove(tr)
        return LessonOutputSchema(**LessonSchema.from_orm(lesson).dict())

    @staticmethod
    async def get_guid(db: AsyncSession, schemas: LessonCreateSchema) -> UUID4:
        lesson = await LessonRepository.get_id(db, schemas)
        if lesson is None:
            raise HTTPException(404, "Занятие не найдено")
        return lesson

    @staticmethod
    async def get_by_group(db: AsyncSession, group: str, lang: str) -> dict:
        lessons = await LessonRepository.get_by_group(db, group, lang)
        if not lessons:
            raise HTTPException(404, "Занятий не найдено")

        teacher_lang = "ru" if lang == "ru" else "en"
        for lesson in lessons:
            lesson.trans = [tr for tr in lesson.trans if tr.lang == lang]
            for teacher in lesson.teachers:
                teacher.trans = [tr for tr in teacher.trans if tr.lang == teacher_lang]

        lessons = [LessonOutputSchema(**LessonSchema.from_orm(lesson).dict()) for lesson in lessons]
        res = LessonsByGroupSchema(lessons=lessons, group=group, lang=lang)
        return res.dict()

    @staticmethod
    async def get_by_teacher(db: AsyncSession, teacher: str, lang: str) -> dict:
        lessons = await LessonRepository.get_by_teacher(db, teacher, lang)
        if not lessons:
            raise HTTPException(404, "Занятий не найдено")

        teacher_lang = "ru" if lang == "ru" else "en"
        teacher_model = await TeacherRepository.get_by_name(db, teacher)
        teacher_model.trans = [tr for tr in teacher_model.trans if tr.lang == teacher_lang]

        for lesson in lessons:
            lesson.trans = [tr for tr in lesson.trans if tr.lang == lang]
            for teacher_ in lesson.teachers:
                teacher_.trans = [tr for tr in teacher_.trans if tr.lang == teacher_lang]

        lessons = [LessonOutputSchema(**LessonSchema.from_orm(lesson).dict()) for lesson in lessons]
        res = LessonsByTeacherSchema(lessons=lessons, teacher=teacher_model, lang=lang)
        return res.dict()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: LessonCreateSchema) -> LessonOutputSchema:
        lesson = await LessonRepository.update(db, guid, schemas)
        if lesson is None:
            raise HTTPException(404, "Занятие не найдено")
        trans = lesson.trans
        for tr in trans:
            if tr.lang != schemas.lang:
                lesson.trans.remove(tr)
        return LessonOutputSchema(**LessonSchema.from_orm(lesson).dict())

    @staticmethod
    async def update_translate(db: AsyncSession, schemas: LessonCreateSchema, guid: UUID4) -> LessonOutputSchema:
        lesson = await LessonRepository.update_translate(db, schemas, guid)
        if lesson is None:
            raise HTTPException(404, "Занятие не найдено")

        trans = lesson.trans
        for tr in trans:
            if tr.lang != schemas.lang:
                lesson.trans.remove(tr)

        return LessonOutputSchema(**LessonSchema.from_orm(lesson).dict())

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response:
        await LessonRepository.delete(db, guid)
        return Response(status_code=204)
