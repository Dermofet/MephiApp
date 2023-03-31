from __future__ import annotations

from datetime import date, time
from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import and_, between, delete, exists, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.association_tables import AT_lesson_group, AT_lesson_room, AT_lesson_teacher
from backend.database.models.group import GroupModel
from backend.database.models.lesson import LessonModel
from backend.database.models.lesson_translate import LessonTranslateModel
from backend.database.models.room import RoomModel
from backend.database.models.teacher import TeacherModel
from backend.database.models.teacher_translate import TeacherTranslateModel
from backend.repositories.group import GroupRepository
from backend.repositories.lesson_translate import LessonTranslateRepository
from backend.repositories.room import RoomRepository
from backend.repositories.teacher import TeacherRepository
from backend.schemas.lesson import LessonCreateSchema, LessonOutputSchema, LessonSchema


class LessonRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: LessonCreateSchema) -> LessonModel:
        lesson = LessonModel(time_start=schemas.time_start,
                             time_end=schemas.time_end,
                             dot=schemas.dot,
                             weeks=schemas.weeks,
                             day=schemas.day,
                             date_start=schemas.date_start,
                             date_end=schemas.date_end)

        lesson = await LessonRepository.set_dependencies(db,
                                                         lesson,
                                                         group=schemas.group,
                                                         room=schemas.room,
                                                         teacher_name=schemas.teacher_name,
                                                         lang=schemas.lang)

        db.add(lesson)
        await db.commit()
        await db.refresh(lesson)

        return lesson

    @staticmethod
    async def set_dependencies(db: AsyncSession,
                               lesson: LessonModel,
                               group: str,
                               room: str,
                               teacher_name: str,
                               lang: str) -> LessonModel:
        group = await GroupRepository.get_by_name(db, group)
        if group is not None:
            lesson.groups.append(group)

        room = await RoomRepository.get_by_number(db, room)
        if room is not None:
            lesson.rooms.append(room)

        teacher = await TeacherRepository.get_by_name(db, teacher_name, lang)
        if teacher is not None:
            lesson.teachers.append(teacher)

        return lesson

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> LessonModel:
        lesson = await db.execute(select(LessonModel).where(LessonModel.guid == guid).limit(1))
        return lesson.scalar()

    @staticmethod
    async def get_unique(db: AsyncSession, schemas: LessonCreateSchema) -> LessonModel:
        lesson_translate_subq = (
            select(LessonTranslateModel.lesson_guid)
            .where(
                (LessonTranslateModel.name == schemas.name) &
                (LessonTranslateModel.subgroup == schemas.subgroup) &
                (LessonTranslateModel.type == schemas.type) &
                (LessonTranslateModel.lang == schemas.lang)
            )
            .limit(1)
            .subquery()
        )

        teacher_translate_subq = (
            select(TeacherTranslateModel.teacher_guid)
            .where(
                (TeacherTranslateModel.name == schemas.teacher_name) &
                (TeacherTranslateModel.lang == schemas.lang)
            )
            .limit(1)
            .subquery()
        )

        group_subq = (
            select(GroupModel.guid)
            .where(GroupModel.name == schemas.group)
            .limit(1)
            .subquery()
        )

        room_subq = (
            select(RoomModel.guid)
            .where(RoomModel.number == schemas.room)
            .limit(1)
            .subquery()
        )

        lesson_query = (
            select(LessonModel)
            .join(AT_lesson_room, LessonModel.guid == AT_lesson_room.c.lesson_guid)
            .join(AT_lesson_group, LessonModel.guid == AT_lesson_group.c.lesson_guid)
            .join(AT_lesson_teacher, LessonModel.guid == AT_lesson_teacher.c.lesson_guid)
            .join(lesson_translate_subq, LessonModel.guid == lesson_translate_subq.c.lesson_guid)
            .where(
                (LessonModel.time_start == schemas.time_start) &
                (LessonModel.time_end == schemas.time_end) &
                (LessonModel.dot == schemas.dot) &
                (LessonModel.weeks == schemas.weeks) &
                (LessonModel.date_start == schemas.date_start) &
                (LessonModel.date_end == schemas.date_end) &
                (LessonModel.day == schemas.day) &
                (AT_lesson_room.c.room_guid == room_subq) &
                (AT_lesson_group.c.group_guid == group_subq) &
                (AT_lesson_teacher.c.teacher_guid == teacher_translate_subq)
            )
            .limit(1)
        )

        lesson = await db.execute(lesson_query)
        return lesson.scalar()

    @staticmethod
    async def get_lesson(db: AsyncSession, schemas: LessonCreateSchema) -> LessonModel:
        lesson_translate_subq = (
            select(LessonTranslateModel.lesson_guid)
            .where(
                (LessonTranslateModel.name == schemas.name) &
                (LessonTranslateModel.subgroup == schemas.subgroup) &
                (LessonTranslateModel.type == schemas.type) &
                (LessonTranslateModel.lang == schemas.lang)
            )
            .limit(1)
            .scalar_subquery()
        )

        room_subq = (
            select(RoomModel.guid)
            .where(RoomModel.number == schemas.room)
            .limit(1)
            .scalar_subquery()
        )

        lesson_room_subq = (
            select(AT_lesson_room.c.lesson_guid)
            .where(AT_lesson_room.c.room_guid == room_subq)
            .limit(1)
            .scalar_subquery()
        )

        lesson_query = (
            select(LessonModel)
            .join(
                lesson_translate_subq,
                LessonModel.guid == lesson_translate_subq
            )
            .join(
                lesson_room_subq,
                LessonModel.guid == lesson_room_subq
            )
            .where(
                (LessonModel.time_start == schemas.time_start) &
                (LessonModel.time_end == schemas.time_end) &
                (LessonModel.dot == schemas.dot) &
                (LessonModel.weeks == schemas.weeks) &
                (LessonModel.date_start == schemas.date_start) &
                (LessonModel.date_end == schemas.date_end) &
                (LessonModel.day == schemas.day)
            )
            .limit(1)
        )

        lesson = await db.scalar(lesson_query)
        return lesson

    @staticmethod
    async def get_id(db: AsyncSession, schemas: LessonCreateSchema) -> UUID4:
        lesson_translate_subq = (
            select(LessonTranslateModel.lesson_guid)
            .where(
                (LessonTranslateModel.name == schemas.name) &
                (LessonTranslateModel.subgroup == schemas.subgroup) &
                (LessonTranslateModel.type == schemas.type) &
                (LessonTranslateModel.lang == schemas.lang)
            )
            .limit(1)
            .subquery()
        )

        room_subq = (
            select(RoomModel.guid)
            .where(RoomModel.number == schemas.room)
            .limit(1)
            .scalar_subquery()
        )

        lesson_room_subq = (
            select(AT_lesson_room.c.lesson_guid)
            .where(AT_lesson_room.c.room_guid == room_subq)
            .subquery()
        )

        lesson_query = (
            select(LessonModel.guid)
            .join(lesson_translate_subq, LessonModel.guid == lesson_translate_subq.c.lesson_guid)
            .join(lesson_room_subq, LessonModel.guid == lesson_room_subq.c.lesson_guid)
            .where(
                (LessonModel.time_start == schemas.time_start) &
                (LessonModel.time_end == schemas.time_end) &
                (LessonModel.dot == schemas.dot) &
                (LessonModel.weeks == schemas.weeks) &
                (LessonModel.date_start == schemas.date_start) &
                (LessonModel.date_end == schemas.date_end) &
                (LessonModel.day == schemas.day)
            )
            .limit(1)
        )

        lesson = await db.execute(lesson_query)
        return lesson.scalar()

    @staticmethod
    async def get_by_group(db: AsyncSession, group: str, lang: str, date_: date = date.today()) -> List[LessonModel]:
        lessons = await db.execute(select(LessonModel)
                                   .join(LessonTranslateModel,
                                         LessonTranslateModel.lesson_guid == LessonModel.guid)
                                   .join(AT_lesson_group,
                                         AT_lesson_group.c.lesson_guid == LessonModel.guid)
                                   .join(GroupModel,
                                         GroupModel.guid == AT_lesson_group.c.group_guid)
                                   .where(GroupModel.name == group and
                                          LessonTranslateModel.lang == lang and
                                          (LessonModel.date_start <= date_ <= LessonModel.date_end)))
        return lessons.scalars().unique().all()

    @staticmethod
    async def get_by_teacher(db: AsyncSession, teacher: str, lang: str, date_: date = date.today()) -> \
            List[LessonModel]:
        lessons = await db.execute(select(LessonModel)
                                   .join(AT_lesson_teacher, AT_lesson_teacher.c.lesson_guid == LessonModel.guid)
                                   .join(TeacherTranslateModel,
                                         TeacherTranslateModel.teacher_guid == AT_lesson_teacher.c.teacher_guid)
                                   .where(TeacherTranslateModel.name == teacher and
                                          TeacherTranslateModel.lang == lang and
                                          and_(
                                              LessonModel.date_start is not None,
                                              and_(
                                                  LessonModel.date_end is not None,
                                                  between(date_, LessonModel.date_start, LessonModel.date_end)
                                              )
                                          )))
        return lessons.scalars().unique().all()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: LessonCreateSchema) -> LessonModel:
        lesson = await LessonRepository.get_by_id(db, guid)
        lesson_translate = await LessonTranslateRepository.get_by_name(db, schemas.name, schemas.lang)

        if lesson is None:
            HTTPException(status_code=404, detail="Занятие не найдено")

        if lesson_translate is None:
            HTTPException(status_code=404, detail="Перевода занятия не существует")

        await db.execute(update(LessonModel).where(LessonModel.guid == guid).values(time_start=schemas.time_start,
                                                                                    time_end=schemas.time_end,
                                                                                    dot=schemas.dot,
                                                                                    weeks=schemas.weeks,
                                                                                    date_start=schemas.date_start,
                                                                                    date_end=schemas.date_end,
                                                                                    day=schemas.day))
        await db.execute(update(LessonModel).where(LessonTranslateModel.guid == lesson_translate.guid)
                         .values(type=schemas.type,
                                 name=schemas.name,
                                 subgroup=schemas.subgroup,
                                 lang=schemas.lang))
        await db.commit()
        await db.refresh(lesson)

        return lesson

    @staticmethod
    async def update_translate(db: AsyncSession, schemas: LessonCreateSchema, guid: str) -> LessonModel:
        lesson = await LessonRepository.get_by_id(db, guid)

        if lesson is None:
            HTTPException(status_code=404, detail="Занятие не найдено")

        for trans in lesson.trans:
            if trans.lang == schemas.lang:
                HTTPException(status_code=404, detail="Занятие на этом языке существует")

        trans = LessonTranslateModel(type=schemas.type,
                                     name=schemas.name,
                                     subgroup=schemas.subgroup,
                                     lang=schemas.lang,
                                     lesson_guid=lesson.guid)
        lesson.trans.append(trans)

        await db.commit()
        await db.refresh(lesson)

        return lesson

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(LessonModel).where(LessonModel.guid == guid))
        await db.commit()
