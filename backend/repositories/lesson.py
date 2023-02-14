from __future__ import annotations

from datetime import date, time
from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.association_tables import *
from backend.database.models.corps import CorpsModel
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
from backend.schemas.lesson import LessonCreateSchema, LessonOutputSchema


class LessonRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: LessonModelCreateSchema) -> LessonModel:
        lesson = LessonModel(time_start=schemas.time_start,
                             time_end=schemas.time_end,
                             dot=schemas.dot,
                             weeks=schemas.weeks,
                             day=schemas.day,
                             date_start=schemas.date_start,
                             date_end=schemas.date_end)

        db.add(lesson)
        await db.commit()

        group = await GroupRepository.get_by_name(db, schemas.group)
        if group is not None:
            lesson.groups.append(group)

        room = await RoomRepository.get_by_number(db, schemas.room)
        if room is not None:
            lesson.rooms.append(room)

        teacher = await TeacherRepository.get_by_name(db, schemas.teacher_name, schemas.lang)
        if teacher is not None:
            lesson.teachers.append(teacher)

        await db.commit()
        await db.refresh(lesson)

        return lesson

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> LessonModel:
        lesson = await db.execute(select(LessonModel).where(LessonModel.guid == guid).limit(1))
        return lesson.scalar()

    @staticmethod
    async def get_unique(db: AsyncSession, schemas: LessonModelCreateSchema) -> LessonModel:
        lesson = await db.execute(select(LessonModel)
                                  .join(AT_lesson_room,
                                        AT_lesson_room.c.lesson_guid == LessonModel.guid)
                                  .join(RoomModel,
                                        RoomModel.guid == AT_lesson_room.c.room_guid)
                                  .join(LessonTranslateModel,
                                        LessonTranslateModel.lesson_guid == LessonModel.guid)
                                  .where(LessonModel.time_start == schemas.time_start and
                                         LessonModel.time_end == schemas.time_end and
                                         LessonModel.dot == schemas.dot and
                                         LessonModel.weeks == schemas.weeks and
                                         LessonModel.date_start == schemas.date_start and
                                         LessonModel.date_end == schemas.date_end and
                                         LessonModel.day == schemas.day and
                                         RoomModel.number == schemas.room and
                                         LessonTranslateModel.name == schemas.name and
                                         LessonTranslateModel.subgroup == schemas.subgroup and
                                         LessonTranslateModel.type == schemas.type and
                                         LessonTranslateModel.lang == schemas.lang).limit(1))
        return lesson.scalar()

    @staticmethod
    async def get_by_group(db: AsyncSession, group: str, lang: str) -> List[LessonTranslateModel]:
        lesson_tr = await db.execute(select(LessonTranslateModel)
                                     .join(LessonModel,
                                           LessonModel.guid == LessonTranslateModel.lesson_guid)
                                     .join(AT_lesson_group,
                                           AT_lesson_group.c.lesson_guid == LessonModel.guid)
                                     .join(GroupModel,
                                           GroupModel.guid == AT_lesson_group.c.group_guid)
                                     .where(GroupModel.name == group and LessonTranslateModel.lang == lang))
        return lesson_tr.scalars().unique().all()

    @staticmethod
    async def get_by_teacher(db: AsyncSession, teacher: str, lang: str) -> List[LessonModel]:
        lesson = await db.execute(select(LessonModel)
                                  .join(AT_lesson_teacher,
                                        AT_lesson_teacher.c.lesson_guid == LessonModel.guid)
                                  .join(TeacherModel,
                                        TeacherModel.guid == AT_lesson_teacher.c.teacher_guid)
                                  .join(TeacherTranslateModel,
                                        TeacherTranslateModel.teacher_guid == TeacherModel.guid)
                                  .join(LessonTranslateModel,
                                        LessonTranslateModel.lesson_guid == LessonModel.guid)
                                  .where(TeacherTranslateModel.lang == lang and
                                         TeacherTranslateModel.name == teacher and
                                         LessonTranslateModel.lang == lang))
        return lesson.scalars().unique().all()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: LessonModelCreateSchema) -> LessonModel:
        lesson = await LessonRepository.get_by_id(db, guid)
        lesson_translate = await LessonTranslateRepository.get_by_id(db, guid=guid)

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
        await db.execute(update(LessonModel).where(LessonTranslateModel.guid == lesson_translate.guid).values(
            type=schemas.type,
            name=schemas.name,
            subgroup=schemas.subgroup,
            lang=schemas.lang))
        await db.commit()
        await db.refresh(lesson)

        return lesson

    @staticmethod
    async def patch(db: AsyncSession, guid: UUID4, schemas: LessonModelCreateSchema) -> LessonModel:
        lesson = await LessonRepository.get_by_id(db, guid)
        lesson_translate = await LessonTranslateRepository.get_unique(db,
                                                                      type_=schemas.type,
                                                                      name=schemas.name,
                                                                      subgroup=schemas.subgroup,
                                                                      lang=schemas.lang)

        # print(f'Patch LessonModel: {LessonModel}')
        # print(f'Patch LessonTranslateModel: {LessonTranslateModel}')

        if lesson is None:
            HTTPException(status_code=404, detail="Занятие не найдено")

        if lesson_translate is None:
            HTTPException(status_code=404, detail="Перевода занятия не существует")

        if not schemas.dict(exclude_unset=True):
            HTTPException(status_code=400, detail="Должно быть задано хотя бы одно новое поле модели")

        modelGroup = await GroupRepository.get_by_name(db, schemas.group)
        groups = lesson.groups
        for group in lesson.groups:
            if group.name == schemas.group:
                groups.append(modelGroup)

        modelRoom = await RoomRepository.get_by_number(db, schemas.room)
        rooms = lesson.rooms
        for room in lesson.rooms:
            if room.number == schemas.room:
                rooms.append(modelRoom)

        modelTeacher = await TeacherRepository.get_by_name(db, schemas.teacher_name, schemas.lang)
        teachers = lesson.teachers
        for teacher in LessonModel.teachers:
            for trans in teacher.trans:
                if trans.name == schemas.teacher_name:
                    teachers.append(modelTeacher)

        await db.execute(update(LessonModel).where(LessonModel.guid == guid).values(time_start=schemas.time_start,
                                                                                    time_end=schemas.time_end,
                                                                                    dot=schemas.dot,
                                                                                    weeks=schemas.weeks,
                                                                                    date_start=schemas.date_start,
                                                                                    date_end=schemas.date_end,
                                                                                    day=schemas.day,
                                                                                    groups=groups,
                                                                                    rooms=rooms,
                                                                                    teachers=teachers))
        await db.execute(update(LessonTranslateModel).where(LessonTranslateModel.guid == lesson_translate.guid).values(
            type=schemas.type,
            name=schemas.name,
            subgroup=schemas.subgroup,
            lang=schemas.lang))
        await db.commit()
        await db.refresh(lesson)

        return lesson

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(LessonModel).where(LessonModel.guid == guid))
        await db.commit()
