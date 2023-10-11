import datetime
from typing import List, Tuple

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import and_, between, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.database.dao.academic import AcademicDAO
from backend.api.database.dao.group import GroupDAO
from backend.api.database.dao.room import RoomDAO
from backend.api.database.dao.teacher import TeacherDAO
from backend.api.database.models.association_tables import AT_lesson_group, AT_lesson_room, AT_lesson_teacher
from backend.api.database.models.group import GroupModel
from backend.api.database.models.lesson import LessonModel
from backend.api.database.models.lesson_translate import LessonTranslateModel
from backend.api.database.models.room import RoomModel
from backend.api.database.models.teacher import TeacherModel
from backend.api.database.models.teacher_translate import TeacherTranslateModel
from backend.api.schemas.lesson import LessonCreateSchema
from etl.schemas.lesson import LessonLoading


class LessonDAO:
    """
    DAO для работы с расписанием
    """

    _session: AsyncSession
    
    def __init__(self, session: AsyncSession):
        self._session = session

    """
    Создание занятия
    """
    async def create(self, data: LessonCreateSchema) -> LessonModel:
        lesson = LessonModel(
            time_start=data.time_start,
            time_end=data.time_end,
            dot=data.dot,
            weeks=data.weeks,
            day=data.day,
            date_start=data.date_start,
            date_end=data.date_end
        )

        lesson = await self.set_dependencies(
            lesson=lesson,
            groups=[data.group],
            rooms=[data.room],
            teachers=[data.teacher_name]
        )

        self._session.add(lesson)
        await self._session.flush()
        await self._session.refresh(lesson)

        return lesson


    async def _set_dependencies(
            self,
            lesson: LessonModel,
            groups: List[str],
            rooms: List[str],
            teachers: List[str],
    ) -> LessonModel:
        
        group_dao = GroupDAO(self._session)
        room_dao = RoomDAO(self._session)
        teacher_dao = TeacherDAO(self._session)

        for group in groups:
            g = await group_dao.get_by_name(group)
            if g is not None:
                lesson.groups.add(g)

        for room in rooms:
            r = await room_dao.get_by_number(room)
            if r is not None:
                lesson.rooms.add(r)

        for teacher in teachers:
            t = await teacher_dao.get_by_name(teacher)
            if t is not None:
                lesson.teachers.add(t)

        return lesson

    """
    Массовое создание занятий
    """
    async def bulk_insert(self, data: List[LessonLoading]) -> None:
        db_lessons = []

        for lesson in data:
            db_lesson = LessonModel(
                time_start=lesson.time_start,
                time_end=lesson.time_end,
                dot=lesson.dot,
                weeks=lesson.weeks,
                day=lesson.day,
                date_start=lesson.date_start,
                date_end=lesson.date_end,
            )
            for trans in lesson.trans:
                db_lesson.trans.add(
                    LessonTranslateModel(
                        name=trans.name, 
                        subgroup=trans.subgroup, 
                        type=trans.type, 
                        lang=trans.lang,
                    )
                )

            self._session.add(db_lesson)

            db_lesson = await self._set_dependencies(
                lesson=db_lesson,
                groups=lesson.groups,
                rooms=lesson.rooms,
                teachers=lesson.teachers
            )

            db_lessons.append(db_lesson)

        await self._session.flush()

    """
    Получение занятия по id
    """
    async def get_by_id(self, guid: UUID4) -> LessonModel:
        lesson = await self._session.execute(select(LessonModel).where(LessonModel.guid == guid).limit(1))
        return lesson.scalar()

    async def get_all(self, limit: int, offset: int) -> List[LessonModel]:
        lessons = await self._session.execute(select(LessonModel).offset(offset).limit(limit))
        return lessons.scalars().unique().all()

    """
    Получение уникального занятия
    """
    async def get_unique(self, data: LessonCreateSchema) -> LessonModel:
        lesson_translate_subq = (
            select(LessonTranslateModel.lesson_guid)
            .where(
                (LessonTranslateModel.name == data.name) &
                (LessonTranslateModel.subgroup == data.subgroup) &
                (LessonTranslateModel.type == data.type) &
                (LessonTranslateModel.lang == data.lang)
            )
            .limit(1)
            .subquery()
        )

        teacher_subq = (
            select(TeacherModel.guid)
            .where(
                (TeacherModel.name == data.teacher_name) &
                (TeacherModel.lang == data.lang)
            )
            .limit(1)
            .subquery()
        )

        group_subq = (
            select(GroupModel.guid)
            .where(GroupModel.name == data.group)
            .limit(1)
            .subquery()
        )

        room_subq = (
            select(RoomModel.guid)
            .where(RoomModel.number == data.room)
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
                (LessonModel.time_start == data.time_start) &
                (LessonModel.time_end == data.time_end) &
                (LessonModel.dot == data.dot) &
                (LessonModel.weeks == data.weeks) &
                (LessonModel.date_start == data.date_start) &
                (LessonModel.date_end == data.date_end) &
                (LessonModel.day == data.day) &
                (AT_lesson_room.c.room_guid == room_subq) &
                (AT_lesson_group.c.group_guid == group_subq) &
                (AT_lesson_teacher.c.teacher_guid == teacher_subq)
            )
            .limit(1)
        )

        lesson = await self._session.execute(lesson_query)
        return lesson.scalar()

    """
    Получение уникального занятия
    """
    async def get_lesson(self, data: LessonCreateSchema) -> LessonModel:
        lesson_translate_subq = (
            select(LessonTranslateModel.lesson_guid)
            .where(
                (LessonTranslateModel.name == data.name) &
                (LessonTranslateModel.subgroup == data.subgroup) &
                (LessonTranslateModel.type == data.type) &
                (LessonTranslateModel.lang == data.lang)
            )
            .limit(1)
            .scalar_subquery()
        )

        room_subq = (
            select(RoomModel.guid)
            .where(RoomModel.number == data.room)
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
                (LessonModel.time_start == data.time_start) &
                (LessonModel.time_end == data.time_end) &
                (LessonModel.dot == data.dot) &
                (LessonModel.weeks == data.weeks) &
                (LessonModel.date_start == data.date_start) &
                (LessonModel.date_end == data.date_end) &
                (LessonModel.day == data.day)
            )
            .limit(1)
        )

        return await self._session.scalar(lesson_query)

    """
    Получение id занятия
    """
    async def get_id(self, data: LessonCreateSchema) -> UUID4:
        lesson_translate_subq = (
            select(LessonTranslateModel.lesson_guid)
            .where(
                (LessonTranslateModel.name == data.name) &
                (LessonTranslateModel.subgroup == data.subgroup) &
                (LessonTranslateModel.type == data.type) &
                (LessonTranslateModel.lang == data.lang)
            )
            .limit(1)
            .subquery()
        )

        room_subq = (
            select(RoomModel.guid)
            .where(RoomModel.number == data.room)
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
                (LessonModel.time_start == data.time_start) &
                (LessonModel.time_end == data.time_end) &
                (LessonModel.dot == data.dot) &
                (LessonModel.weeks == data.weeks) &
                (LessonModel.date_start == data.date_start) &
                (LessonModel.date_end == data.date_end) &
                (LessonModel.day == data.day)
            )
            .limit(1)
        )

        lesson = await self._session.execute(lesson_query)
        return lesson.scalar()

    """
    Получение занятия по группе
    """
    async def get_by_group(self, group: str, lang: str, date_: datetime.date = datetime.date.today()) -> List[LessonModel]:
        lessons = await self._session.execute(
            select(LessonModel)
            .join(
                LessonTranslateModel,
                LessonTranslateModel.lesson_guid == LessonModel.guid
            )
            .join(
                AT_lesson_group,
                AT_lesson_group.c.lesson_guid == LessonModel.guid
            )
            .join(
                GroupModel,
                GroupModel.guid == AT_lesson_group.c.group_guid
            )
            .where(
                GroupModel.name == group and
                LessonTranslateModel.lang == lang and
                (LessonModel.date_start <= date_ <= LessonModel.date_end)
            )
        )
        return lessons.scalars().unique().all()
    
    async def get_trans(self, lesson: LessonModel, lang: str) -> LessonTranslateModel:
        trans = await self._session.execute(lesson.trans.select().where(LessonTranslateModel.lang == lang))
        return trans.scalars().first()
    
    async def get_teachers(self, lesson: LessonModel, lang: str) -> List[Tuple[TeacherModel, TeacherTranslateModel]]:
        teacher_dao = TeacherDAO(self._session)

        teachers = await self._session.execute(lesson.teachers.select())
        teachers = teachers.scalars().all()

        return [(teacher, await teacher_dao.get_trans(teacher, lang=lang)) for teacher in teachers]
    
    async def get_groups(self, lesson: LessonModel) -> List[GroupModel]:
        group_dao = GroupDAO(self._session)

        groups = await self._session.execute(lesson.groups.select())
        groups = groups.scalars().all()
        for group in groups:
            group.academic = await group_dao.get_academic(group)
        return groups
    
    async def get_rooms(self, lesson: LessonModel) -> List[RoomModel]:
        room_dao = RoomDAO(self._session)

        rooms = await self._session.execute(lesson.rooms.select())
        rooms = rooms.scalars().all()
        for room in rooms:
            room.corps = await room_dao.get_corps(room)
        return rooms

    """
    Получение занятия по преподавателю
    """
    async def get_by_teacher(self, teacher: str, lang: str, date_: datetime.date = datetime.date.today()) -> List[LessonModel]:
        lessons = await self._session.execute(
            select(LessonModel)
            .join(
                AT_lesson_teacher,
                AT_lesson_teacher.c.lesson_guid == LessonModel.guid
            )
            .join(
                TeacherTranslateModel,
                TeacherTranslateModel.teacher_guid == AT_lesson_teacher.c.teacher_guid
            )
            .where(
                TeacherTranslateModel.name == teacher and
                TeacherTranslateModel.lang == lang and
                and_(
                    LessonModel.date_start is not None,
                    and_(
                        LessonModel.date_end is not None,
                        between(date_, LessonModel.date_start, LessonModel.date_end)
                    )
                )
            )
        )
        return lessons.scalars().unique().all()

    """
    Обновление занятия
    """
    async def update(self, guid: UUID4, data: LessonCreateSchema) -> LessonModel:
        lesson = await self.get_by_id(guid)
        lesson_translate = await self.get_by_name_lesson_translate(data.name, data.lang)

        if lesson is None:
            HTTPException(status_code=404, detail="Занятие не найдено")

        if lesson_translate is None:
            HTTPException(status_code=404, detail="Перевода занятия не существует")

        await self._session.execute(
            update(LessonModel)
            .where(LessonModel.guid == guid)
            .values(
                time_start=data.time_start,
                time_end=data.time_end,
                dot=data.dot,
                weeks=data.weeks,
                date_start=data.date_start,
                date_end=data.date_end,
                day=data.day
            )
        )
        await self._session.execute(
            update(LessonModel)
            .where(LessonTranslateModel.guid == lesson_translate.guid)
            .values(
                type=data.type,
                name=data.name,
                subgroup=data.subgroup,
                lang=data.lang
            )
        )
        await self._session.flush()
        await self._session.refresh(lesson)

        return lesson

    """
    Обновление перевода занятия
    """
    async def update_translate(self, data: LessonCreateSchema, guid: str) -> LessonModel:
        lesson = await self.get_by_id(guid)

        if lesson is None:
            HTTPException(status_code=404, detail="Занятие не найдено")

        for trans in lesson.trans:
            if trans.lang == data.lang:
                HTTPException(status_code=404, detail="Занятие на этом языке существует")

        trans = LessonTranslateModel(
            type=data.type,
            name=data.name,
            subgroup=data.subgroup,
            lang=data.lang,
            lesson_guid=lesson.guid
        )
        lesson.trans.append(trans)

        await self._session.flush()
        await self._session.refresh(lesson)

        return lesson

    """
    Удаление занятия
    """
    async def delete(self, guid: UUID4) -> None:
        await self._session.execute(delete(LessonModel).where(LessonModel.guid == guid))
        await self._session.flush()