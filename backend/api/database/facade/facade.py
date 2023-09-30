import datetime
from abc import ABC
from typing import List, Tuple

from fastapi import Depends
from pydantic import UUID4, BaseModel
from sqlalchemy import delete, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.database.connection import get_session
from backend.api.database.dao.academic import AcademicDAO
from backend.api.database.dao.corps import CorpsDAO
from backend.api.database.dao.group import GroupDAO
from backend.api.database.dao.lesson import LessonDAO
from backend.api.database.dao.news import NewsDAO
from backend.api.database.dao.room import RoomDAO
from backend.api.database.dao.start_semester import StartSemesterDAO
from backend.api.database.dao.teacher import TeacherDAO
from backend.api.database.facade.interface import IFacadeDB
from backend.api.database.models import (
    AcademicModel,
    CorpsModel,
    GroupModel,
    LessonModel,
    NewsModel,
    RoomModel,
    StartSemesterModel,
)
from backend.api.database.models.lesson_translate import LessonTranslateModel
from backend.api.database.models.news_image import NewsImageModel
from backend.api.database.models.teacher import TeacherModel
from backend.api.database.models.teacher_translate import TeacherTranslateModel
from backend.api.filters.room import RoomFilter
from backend.api.schemas.academic import AcademicCreateSchema
from backend.api.schemas.corps import CorpsCreateSchema
from backend.api.schemas.group import GroupCreateSchema
from backend.api.schemas.lesson import LessonCreateSchema
from backend.api.schemas.news import NewsCreateSchema
from backend.api.schemas.room import RoomCreateSchema
from backend.api.schemas.start_semester import StartSemesterCreateSchema
from backend.api.schemas.teacher import TeacherCreateSchema
from etl.schemas.lesson import LessonLoading


class FacadeDB(IFacadeDB, ABC):
    _session: AsyncSession

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self._session = session
        self.academic_dao = AcademicDAO(session=session)
        self.corps_dao = CorpsDAO(session=session)
        self.group_dao = GroupDAO(session=session)
        self.lesson_dao = LessonDAO(session=session)
        self.news_dao = NewsDAO(session=session)
        self.room_dao = RoomDAO(session=session)
        self.start_semester_dao = StartSemesterDAO(session=session)
        self.teacher_dao = TeacherDAO(session=session)

    async def is_alive(self) -> bool:
        try:
            await self._session.execute(text("SELECT 1"))
        except Exception:
            return False
        return True

    async def commit(self) -> None:
        await self._session.commit()

    async def refresh(self, model: BaseModel) -> BaseModel:
        await self._session.refresh(model)
        return model

    async def rollback(self) -> None:
        await self._session.rollback()

    # Academic
    async def create_academic(self, data: AcademicCreateSchema) -> AcademicModel:
        return await self.academic_dao.create(data)
    async def bulk_insert_academic(self, data: List[AcademicCreateSchema]) -> None:
        return await self.academic_dao.bulk_insert(data)

    async def get_by_id_academic(self, guid: UUID4) -> AcademicModel:
        return await self.academic_dao.get_by_id(guid)

    async def get_by_name_academic(self, name: str) -> AcademicModel:
        return await self.academic_dao.get_by_name(name)
    
    async def get_all_academics(self) -> List[AcademicModel]:
        return await self.academic_dao.get_all()

    async def update_academic(self, guid: UUID4, data: AcademicCreateSchema) -> AcademicModel:
        return await self.academic_dao.update(guid, data)

    async def delete_academic(self, guid: UUID4) -> None:
        return await self.academic_dao.delete(guid)

    # Corps
    async def create_corps(self, data: CorpsCreateSchema) -> CorpsModel:
        return await self.corps_dao.create(data)

    async def bulk_insert_corps(self, data: List[CorpsCreateSchema]) -> None:
        return await self.corps_dao.bulk_insert(data)

    async def get_by_id_corps(self, guid: UUID4) -> CorpsModel:
        return await self.corps_dao.get_by_id(guid)
    async def get_by_name_corps(self, name: str) -> CorpsModel:
        return await self.corps_dao.get_by_name(name)
    async def get_all_corps(self) -> List[CorpsModel]:
        return await self.corps_dao.get_all()

    async def update_corps(self, guid: UUID4, data: CorpsCreateSchema) -> CorpsModel:
        return await self.corps_dao.update(guid, data)

    async def delete_corps(self, guid: UUID4) -> None:
        return await self.corps_dao.delete(guid)

    # Group
    async def create_group(self, data: GroupCreateSchema, academic_guid: UUID4) -> GroupModel:
        return await self.group_dao.create(data, academic_guid)

    async def bulk_insert_group(self, data: List[GroupCreateSchema]) -> None:
        return await self.group_dao.bulk_insert(data)

    async def get_by_id_group(self, guid: UUID4) -> GroupModel:
        return await self.group_dao.get_by_id(guid)

    async def get_all_group(self) -> List[str]:
        return await self.group_dao.get_all()

    async def get_by_name_group(self, name: str) -> GroupModel:
        return await self.group_dao.get_by_name(name)

    async def get_academic_group(self, group: GroupModel) -> AcademicModel:
        return await self.group_dao.get_academic(group)

    async def update_group(self, guid: UUID4, data: GroupCreateSchema) -> GroupModel:
        return await self.group_dao.update(guid, data)

    async def delete_group(self, guid: UUID4) -> None:
        return await self.group_dao.delete(guid)

    # Lesson
    async def create_lesson(self, data: LessonCreateSchema) -> LessonModel:
        return await self.lesson_dao.create(data)

    async def bulk_insert_lesson(self, data: List[LessonLoading]) -> None:
        return await self.lesson_dao.bulk_insert(data)

    async def get_by_id_lesson(self, guid: UUID4) -> LessonModel:
        return await self.lesson_dao.get_by_id(guid)

    async def get_unique_lesson(self, data: LessonCreateSchema) -> LessonModel:
        return await self.lesson_dao.get_unique(data)

    async def get_lesson_lesson(self, data: LessonCreateSchema) -> LessonModel:
        return await self.lesson_dao.get_lesson(data)

    async def get_id_lesson(self, data: LessonCreateSchema) -> UUID4:
        return await self.lesson_dao.get_id(data)

    async def get_trans_lesson(self, lesson: LessonModel, lang: str) -> LessonTranslateModel:
        return await self.lesson_dao.get_trans(lesson, lang)

    async def get_teachers_lesson(self, lesson: LessonModel, lang: str) -> List[Tuple[TeacherModel, TeacherTranslateModel]]:
        return await self.lesson_dao.get_teachers(lesson, lang)

    async def get_groups_lesson(self, lesson: LessonModel) -> List[GroupModel]:
        return await self.lesson_dao.get_groups(lesson)

    async def get_rooms_lesson(self, lesson: LessonModel) -> List[RoomModel]:
        return await self.lesson_dao.get_rooms(lesson)

    async def get_by_group_lesson(self, group: str, lang: str, date_: datetime.date = datetime.date.today()) -> \
            List[LessonModel]:
        return await self.lesson_dao.get_by_group(group, lang, date_)

    async def get_by_teacher_lesson(self, teacher: str, lang: str, date_: datetime.date = datetime.date.today()) -> \
            List[LessonModel]:
        return await self.lesson_dao.get_by_teacher(teacher, lang, date_)

    async def update_lesson(self, guid: UUID4, data: LessonCreateSchema) -> LessonModel:
        return await self.lesson_dao.update(guid, data)

    async def update_translate_lesson(self, data: LessonCreateSchema, guid: str) -> LessonModel:
        return await self.lesson_dao.update_translate(data, guid)

    async def delete_lesson(self, guid: UUID4) -> None:
        return await self.lesson_dao.delete(guid)

    # News
    async def get_by_id_news(self, guid: UUID4) -> NewsModel:
        return await self.news_dao.get_by_id(guid)

    async def get_by_news_id_news(self, news_id: str) -> NewsModel:
        return await self.news_dao.get_by_news_id(news_id)
    
    async def get_images_news(self, news: NewsModel) -> List[NewsImageModel]:
        return await self.news_dao.get_images(news)

    async def get_all_news(self, tag: str, offset: int, limit: int = 100) -> List[NewsModel]:
        return await self.news_dao.get_all(tag, offset, limit)

    async def bulk_insert_news(self, data: List[NewsCreateSchema]) -> None:
        return await self.news_dao.bulk_insert(data)

    async def delete_news(self, guid: UUID4) -> None:
        return await self.news_dao.delete(guid)

    # Room
    async def create_room(self, data: RoomCreateSchema, corps_guid) -> RoomModel:
        return await self.room_dao.create(data, corps_guid)

    async def bulk_insert_room(self, data: List[RoomCreateSchema]) -> None:
        return await self.room_dao.bulk_insert(data)

    async def get_by_id_room(self, guid: UUID4) -> RoomModel:
        return await self.room_dao.get_by_id(guid)

    async def get_all_room(self) -> List[RoomModel]:
        return await self.room_dao.get_all()

    async def get_by_number_room(self, number: str) -> RoomModel:
        return await self.room_dao.get_by_number(number)

    async def get_empty_room(self, room_filter: RoomFilter, corps: List[str]) -> List[Tuple[str, datetime.time, datetime.time, str]]:
        return await self.room_dao.get_empty(room_filter, corps)

    async def update_room(self, guid: UUID4, data: RoomCreateSchema) -> RoomModel:
        return await self.room_dao.update(guid, data)

    async def delete_room(self, guid: UUID4) -> None:
        return await self.room_dao.delete(guid)

    # Start semester
    async def create_start_semester(self, data: StartSemesterCreateSchema) -> StartSemesterModel:
        return await self.start_semester_dao.create(data)

    async def get_start_semester(self) -> StartSemesterModel:
        return await self.start_semester_dao.get()

    async def update_start_semester(self, data: StartSemesterCreateSchema) -> StartSemesterModel:
        return await self.start_semester_dao.update(data)

    # Teacher
    async def create_teacher(self, data: TeacherCreateSchema) -> TeacherModel:
        return await self.teacher_dao.create(data)

    async def bulk_insert_teacher(self, data: List[TeacherCreateSchema]) -> None:
        return await self.teacher_dao.bulk_insert(data)

    async def get_by_id_teacher(self, guid: UUID4) -> TeacherModel:
        return await self.teacher_dao.get_by_id(guid)

    async def get_all_teacher(self, lang: str) -> List[str]:
        return await self.teacher_dao.get_all(lang)

    async def get_by_name_teacher(self, name: str) -> TeacherModel:
        return await self.teacher_dao.get_by_name(name)

    async def get_unique_teacher(self, data: TeacherCreateSchema) -> TeacherModel:
        return await self.teacher_dao.get_unique(data)

    async def get_trans_teacher(self, teacher: TeacherModel, lang: str) -> TeacherTranslateModel:
        return await self.teacher_dao.get_trans(teacher, lang)

    async def update_teacher(self, guid: UUID4, data: TeacherCreateSchema) -> TeacherModel:
        return await self.teacher_dao.update(guid, data)

    async def delete_teacher(self, guid: UUID4) -> None:
        return await self.teacher_dao.delete(guid)
