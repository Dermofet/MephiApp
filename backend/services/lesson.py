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
from backend.schemas.lesson import LessonCreateSchema, LessonOutputSchema, LessonSchema
from backend.schemas.lesson_translate import (
    LessonTranslateCreateSchema,
    LessonTranslateOutputSchema,
    LessonTranslateSchema,
)


class LessonService:
    @staticmethod
    async def create(db: AsyncSession, schemas: LessonCreateSchema) -> LessonTranslateOutputSchema:
        lesson = await LessonRepository.get_unique(db, schemas)
        if lesson is not None:
            await LessonRepository.patch(db, lesson.guid, schemas)
            lesson_translate = await LessonTranslateRepository.get_by_name(db, schemas.name, schemas.lang)
            print("Patch lesson")
        else:
            lesson = await LessonRepository.create(db, schemas)

            # group = await GroupRepository.get_by_name(db, schemas.group)
            # if group is not None:
            #     await db.execute(insert(AT_lesson_group).values({
            #         "lesson_guid": lesson.guid,
            #         "group_guid": group.guid
            #     }))
            #
            # room = await RoomRepository.get_by_number(db, schemas.room)
            # if room is not None:
            #     await db.execute(insert(AT_lesson_room).values({
            #         "lesson_guid": lesson.guid,
            #         "room_guid": room.guid
            #     }))
            #
            # teacher = await TeacherRepository.get_by_name(db, schemas.teacher_name, schemas.lang)
            # if teacher is not None:
            #     await db.execute(insert(AT_lesson_teacher).values({
            #         "lesson_guid": lesson.guid,
            #         "teacher_guid": teacher.guid
            #     }))
            #
            # await db.commit()

            print(f'Lesson: {LessonSchema.from_orm(lesson).dict()}')
            lesson_translate = await LessonTranslateRepository.create(db,
                                                                      LessonTranslateCreateSchema(
                                                                          type=schemas.type,
                                                                          name=schemas.name,
                                                                          subgroup=schemas.subgroup,
                                                                          lang=schemas.lang,
                                                                          lesson_guid=lesson.guid)
                                                                      )
            print(f'LessonTranslate: {LessonTranslateSchema.from_orm(lesson).dict()}')
            print("Create lesson")
        return LessonTranslateOutputSchema(**LessonTranslateSchema.from_orm(lesson_translate).dict())

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> LessonOutputSchema:
        lesson = await LessonRepository.get_by_id(db, guid)
        if lesson is None:
            raise HTTPException(404, "Занятие не найдено")
        return LessonOutputSchema(**LessonSchema.from_orm(lesson).dict())

    @staticmethod
    async def get_by_group(db: AsyncSession, group: str, lang: str) -> list[LessonTranslateOutputSchema]:
        lessons = await LessonRepository.get_by_group(db, group, lang)
        print(lessons)
        if len(lessons) == 0:
            raise HTTPException(404, "Занятие не найдено")
        results = [LessonTranslateSchema.from_orm(lesson) for lesson in lessons]
        return [LessonTranslateOutputSchema(**result.dict()) for result in results]

    @staticmethod
    async def get_by_teacher(db: AsyncSession, teacher: str, lang: str) -> list[LessonOutputSchema]:
        lessons = await LessonRepository.get_by_teacher(db, teacher, lang)
        if lessons is None:
            raise HTTPException(404, "Занятие не найдено")
        results = [LessonSchema.from_orm(lesson) for lesson in lessons]
        return [LessonTranslateOutputSchema(**result.dict()) for result in results]

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: LessonCreateSchema) -> LessonOutputSchema:
        lesson = await LessonRepository.update(db, guid, schemas)
        if lesson is None:
            raise HTTPException(404, "Занятие не найдено")
        result = LessonSchema.from_orm(lesson)
        return LessonOutputSchema(**result.dict())

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await LessonRepository.delete(db, guid)
        return Response(status_code=204)
