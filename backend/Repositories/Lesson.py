from datetime import date, time
from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.DataBase.Models.Language import Language
from backend.DataBase.Models.Lesson import Lesson
from backend.DataBase.Models.LessonTranslate import LessonTranslate
from backend.DataBase.Models.Room import Room
from backend.Schemas.Lesson import LessonCreate, LessonOutput


class LessonRepository:
    @staticmethod
    async def create(
            db: AsyncSession,
            schemas: LessonCreate,
            room_guid: UUID4,
            group_guid: UUID4,
            teacher_guid: UUID4,
            lesson_translate_guid: UUID4) -> Lesson:
        lesson = Lesson(time_start=schemas.time_start,
                        time_end=schemas.time_end,
                        dot=schemas.dot,
                        weeks=schemas.weeks,
                        day=schemas.day,
                        date_start=schemas.date_start,
                        date_end=schemas.date_end,
                        room_guid=room_guid,
                        group_guid=group_guid,
                        teacher_guid=teacher_guid,
                        lesson_translate_guid=lesson_translate_guid)
        db.add(lesson)
        await db.commit()
        await db.refresh(lesson)
        return lesson

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> Lesson:
        lesson = await db.execute(select(Lesson).where(Lesson.guid == guid).limit(1))
        if len(lesson.scalars().all()) > 0:
            return lesson.scalars().all()[0]
        return None

    @staticmethod
    async def get_unique(db: AsyncSession, schemas: LessonCreate) -> Lesson:
        lesson = await db.execute(select(Lesson)
                                  .join(Language,
                                        Language.lang == schemas.lang)
                                  .join(LessonTranslate,
                                        LessonTranslate.name == schemas.name and
                                        LessonTranslate.type == schemas.type and
                                        LessonTranslate.subgroup == schemas.subgroup and
                                        LessonTranslate.lang_guid == Language.guid)
                                  .join(Room,
                                        Room.number == schemas.room)
                                  .where(Lesson.time_start == schemas.time_start and
                                         Lesson.time_end == schemas.time_end and
                                         Lesson.dot == schemas.dot and
                                         Lesson.weeks == schemas.weeks and
                                         Lesson.date_start == schemas.date_start and
                                         Lesson.date_end == schemas.date_end and
                                         Lesson.day == schemas.day and
                                         Lesson.room_guid == Room.guid and
                                         Lesson.group_guid == Group.guid and
                                         Lesson.lesson_translate_guid == LessonTranslate.guid).limit(1))
        if len(lesson.scalars().all()) > 0:
            return lesson.scalars().all()[0]
        return None

    @staticmethod
    async def get_by_group(db: AsyncSession, group: str) -> List[Lesson]:
        lessons = await db.execute(select(Lesson).where(Lesson.group_name == group))
        return lessons.scalars().unique().all()

    @staticmethod
    async def get_by_teacher(db: AsyncSession, teacher_guid: UUID4) -> List[Lesson]:
        lessons = await db.execute(select(Lesson)
                                   .join(LessonTeacher,
                                         LessonTeacher.teacher_guid == teacher_guid)
                                   .where(Lesson.guid == LessonTeacher.lesson_guid))
        return lessons.scalars().unique().all()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: LessonCreate) -> Lesson:
        lesson = await LessonRepository.get_by_id(db, guid)

        if lesson is None:
            HTTPException(status_code=404, detail="Занятие не найдено")

        await db.execute(update(Lesson).where(Lesson.guid == guid).values(**schemas.dict()))
        await db.commit()
        await db.refresh(lesson)

        return lesson

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(Lesson).where(Lesson.guid == guid))
        await db.commit()
