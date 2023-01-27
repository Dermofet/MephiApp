from __future__ import annotations

from datetime import date, time
from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.DataBase.Models.AssociationTables import *
from backend.DataBase.Models.Group import Group

# from backend.DataBase.Models.Language import Language
from backend.DataBase.Models.Lesson import Lesson
from backend.DataBase.Models.LessonTranslate import LessonTranslate
from backend.DataBase.Models.Room import Room
from backend.DataBase.Models.Teacher import Teacher
from backend.DataBase.Models.TeacherTranslate import TeacherTranslate
from backend.Schemas.Lesson import LessonCreate, LessonOutput


class LessonRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: LessonCreate) -> Lesson:
        lesson = Lesson(time_start=schemas.time_start,
                        time_end=schemas.time_end,
                        dot=schemas.dot,
                        weeks=schemas.weeks,
                        day=schemas.day,
                        date_start=schemas.date_start,
                        date_end=schemas.date_end)
        db.add(lesson)
        await db.commit()
        await db.refresh(lesson)
        return lesson

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4, lang: str) -> Lesson:
        lesson = await db.execute(select(Lesson)
                                  .where(Lesson.guid == guid).limit(1))
        return lesson.scalar()

    @staticmethod
    async def get_unique(db: AsyncSession, schemas: LessonCreate) -> Lesson:
        lesson = await db.execute(select(Lesson)
                                  .join(Group,
                                        Group.name == schemas.group)
                                  .join(AT_lesson_group,
                                        AT_lesson_group.c.group_guid == Group.guid)
                                  .join(Room,
                                        Room.number == schemas.room)
                                  .join(AT_lesson_room,
                                        AT_lesson_room.c.room_guid == Room.guid)
                                  .join(TeacherTranslate,
                                        TeacherTranslate.lang == schemas.lang,
                                        TeacherTranslate.name == schemas.teacher_name)
                                  .join(Teacher,
                                        Teacher.guid == TeacherTranslate.teacher_guid)
                                  .join(AT_lesson_teacher,
                                        AT_lesson_teacher.c.teacher_guid == TeacherTranslate.teacher_guid)
                                  .join(LessonTranslate,
                                        LessonTranslate.lesson_guid == Lesson.guid)
                                  .where(Lesson.time_start == schemas.time_start and
                                         Lesson.time_end == schemas.time_end and
                                         Lesson.dot == schemas.dot and
                                         Lesson.weeks == schemas.weeks and
                                         Lesson.date_start == schemas.date_start and
                                         Lesson.date_end == schemas.date_end and
                                         Lesson.day == schemas.day and
                                         Lesson.guid == AT_lesson_group.c.lesson_guid and
                                         Lesson.guid == AT_lesson_room.c.lesson_guid and
                                         Lesson.guid == AT_lesson_teacher.c.lesson_guid).limit(1))
        return lesson.scalar()

    @staticmethod
    async def get_by_group(db: AsyncSession, group: str, lang: str) -> List[Lesson]:
        lessons = await db.execute(select(Lesson)
                                   .join(Group,
                                         Group.name == group)
                                   .join(AT_lesson_group,
                                         AT_lesson_group.c.group_guid == Group.guid)
                                   .join(LessonTranslate,
                                         LessonTranslate.lang == lang,
                                         Lesson.guid == LessonTranslate.lesson_guid)
                                   .where(Lesson.guid == AT_lesson_group.c.lesson_guid))
        return lessons.scalars().unique().all()

    @staticmethod
    async def get_by_teacher(db: AsyncSession, teacher: str, lang: str) -> List[Lesson]:
        lessons = await db.execute(select(Lesson)
                                   .join(TeacherTranslate,
                                         TeacherTranslate.lang == lang,
                                         TeacherTranslate.name == teacher)
                                   .join(Teacher,
                                         Teacher.guid == TeacherTranslate.teacher_guid)
                                   .join(AT_lesson_teacher,
                                         AT_lesson_teacher.c.teacher_guid == TeacherTranslate.teacher_guid)
                                   .join(LessonTranslate,
                                         LessonTranslate.lesson_guid == Lesson.guid,
                                         LessonTranslate.lang == lang)
                                   .where(Lesson.guid == AT_lesson_teacher.c.lesson_guid and
                                          Lesson.guid == LessonTranslate.lesson_guid))
        return lessons.scalars().unique().all()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: LessonCreate) -> Lesson:
        lesson = await LessonRepository.get_by_id(db, guid, schemas.lang)

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
