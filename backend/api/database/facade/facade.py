import datetime
from abc import ABC
from typing import List, Tuple

from pydantic import UUID4, BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

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
from etl.schemas.lesson import LessonLoading, LessonTranslateLoading
from etl.schemas.teacher import TeacherTranslateLoading
from utils.version import Version


class FacadeDB(IFacadeDB, ABC):
    _session: AsyncSession
    _version: Version

    def __init__(self, session: AsyncSession, version: Version):
        self._version = version
        self._session = session

    async def is_alive(self) -> bool:
        try:
            await self._session.execute(text("SELECT 1"))
        except Exception:
            return False
        return True

    async def commit(self) -> None:
        if self._version >= "0.0.1":
            await self._session.commit()

    async def flush(self) -> None:
        if self._version >= "0.0.1":
            await self._session.flush()

    async def refresh(self, model: BaseModel) -> BaseModel:
        if self._version >= "0.0.1":
            await self._session.refresh(model)
        return model

    async def rollback(self) -> None:
        if self._version >= "0.0.1":
            await self._session.rollback()

    # Academic
    async def create_academic(self, data: AcademicCreateSchema) -> AcademicModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import AcademicDAO

            academic_dao = AcademicDAO(session=self._session)
            return await academic_dao.create(data)

    async def bulk_insert_academic(self, data: List[AcademicCreateSchema]) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import AcademicDAO

            academic_dao = AcademicDAO(session=self._session)
            return await academic_dao.bulk_insert(data)

    async def get_by_id_academic(self, guid: UUID4) -> AcademicModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import AcademicDAO

            academic_dao = AcademicDAO(session=self._session)
            return await academic_dao.get_by_id(guid)

    async def get_by_name_academic(self, name: str) -> AcademicModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import AcademicDAO

            academic_dao = AcademicDAO(session=self._session)
            return await academic_dao.get_by_name(name)

    async def get_all_academics(self) -> List[AcademicModel]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import AcademicDAO

            academic_dao = AcademicDAO(session=self._session)
            return await academic_dao.get_all()

    async def update_academic(self, guid: UUID4, data: AcademicCreateSchema) -> AcademicModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import AcademicDAO

            academic_dao = AcademicDAO(session=self._session)
            return await academic_dao.update(guid, data)

    async def delete_academic(self, guid: UUID4) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import AcademicDAO

            academic_dao = AcademicDAO(session=self._session)
            return await academic_dao.delete(guid)

    # Corps
    async def create_corps(self, data: CorpsCreateSchema) -> CorpsModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import CorpsDAO

            corps_dao = CorpsDAO(session=self._session)
            return await corps_dao.create(data)

    async def bulk_insert_corps(self, data: List[CorpsCreateSchema]) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import CorpsDAO

            corps_dao = CorpsDAO(session=self._session)
            return await corps_dao.bulk_insert(data)

    async def get_by_id_corps(self, guid: UUID4) -> CorpsModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import CorpsDAO

            corps_dao = CorpsDAO(session=self._session)
            return await corps_dao.get_by_id(guid)

    async def get_by_name_corps(self, name: str) -> CorpsModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import CorpsDAO

            corps_dao = CorpsDAO(session=self._session)
            return await corps_dao.get_by_name(name)

    async def get_all_corps(self) -> List[CorpsModel]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import CorpsDAO

            corps_dao = CorpsDAO(session=self._session)
            return await corps_dao.get_all()

    async def update_corps(self, guid: UUID4, data: CorpsCreateSchema) -> CorpsModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import CorpsDAO

            corps_dao = CorpsDAO(session=self._session)
            return await corps_dao.update(guid, data)

    async def delete_corps(self, guid: UUID4) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import CorpsDAO

            corps_dao = CorpsDAO(session=self._session)
            return await corps_dao.delete(guid)

    # Group
    async def create_group(self, data: GroupCreateSchema, academic_guid: UUID4) -> GroupModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import GroupDAO

            group_dao = GroupDAO(session=self._session)
            return await group_dao.create(data, academic_guid)

    async def bulk_insert_group(self, data: List[GroupCreateSchema]) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import GroupDAO

            group_dao = GroupDAO(session=self._session)
            return await group_dao.bulk_insert(data)

    async def get_by_id_group(self, guid: UUID4) -> GroupModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import GroupDAO

            group_dao = GroupDAO(session=self._session)
            return await group_dao.get_by_id(guid)

    async def get_all_group(self) -> List[str]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import GroupDAO

            group_dao = GroupDAO(session=self._session)
            return await group_dao.get_all()

    async def get_by_name_group(self, name: str) -> GroupModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import GroupDAO

            group_dao = GroupDAO(session=self._session)
            return await group_dao.get_by_name(name)

    async def get_academic_group(self, group: GroupModel) -> AcademicModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import GroupDAO

            group_dao = GroupDAO(session=self._session)
            return await group_dao.get_academic(group)

    async def update_group(self, guid: UUID4, data: GroupCreateSchema) -> GroupModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import GroupDAO

            group_dao = GroupDAO(session=self._session)
            return await group_dao.update(guid, data)

    async def delete_group(self, guid: UUID4) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import GroupDAO

            group_dao = GroupDAO(session=self._session)
            return await group_dao.delete(guid)

    # Lesson
    async def create_lesson(self, data: LessonCreateSchema) -> LessonModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
            return await lesson_dao.create(data)

    async def bulk_insert_lesson(self, data: List[LessonLoading]) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.bulk_insert(data)

    async def get_by_id_lesson(self, guid: UUID4) -> LessonModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.get_by_id(guid)

    async def get_all_lesson(self, limit: int, offset: int) -> List[LessonModel]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.get_all(limit, offset)

    async def get_all_trans_lesson(self, limit: int, offset: int, lang: str) -> List[LessonModel]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.get_all_trans(limit, offset, lang)

    async def bulk_insert_trans_lesson(self, data: List[LessonTranslateLoading]) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.bulk_insert_trans(data)

    async def get_unique_lesson(self, data: LessonCreateSchema) -> LessonModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.get_unique(data)

    async def get_lesson_lesson(self, data: LessonCreateSchema) -> LessonModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.get_lesson(data)

    async def get_id_lesson(self, data: LessonCreateSchema) -> UUID4:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.get_id(data)

    async def get_trans_lesson(self, lesson: LessonModel, lang: str) -> LessonTranslateModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.get_trans(lesson, lang)

    async def get_teachers_lesson(
        self, lesson: LessonModel, lang: str
    ) -> List[Tuple[TeacherModel, TeacherTranslateModel]]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.get_teachers(lesson, lang)

    async def get_groups_lesson(self, lesson: LessonModel) -> List[GroupModel]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.get_groups(lesson)

    async def get_rooms_lesson(self, lesson: LessonModel) -> List[RoomModel]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.get_rooms(lesson)

    async def get_by_group_lesson(
        self, group: str, lang: str, date_: datetime.date = datetime.date.today()
    ) -> List[LessonModel]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.get_by_group(group, lang, date_)

    async def get_by_teacher_lesson(
        self, teacher: str, lang: str, date_: datetime.date = datetime.date.today()
    ) -> List[LessonModel]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.get_by_teacher(teacher, lang, date_)

    async def update_lesson(self, guid: UUID4, data: LessonCreateSchema) -> LessonModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.update(guid, data)

    async def update_translate_lesson(self, data: LessonCreateSchema, guid: str) -> LessonModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
        return await lesson_dao.update_translate(data, guid)

    async def delete_lesson(self, guid: UUID4) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import LessonDAO

            lesson_dao = LessonDAO(session=self._session)
            return await lesson_dao.delete(guid)

    # News
    async def get_by_id_news(self, guid: UUID4) -> NewsModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import NewsDAO

            news_dao = NewsDAO(session=self._session)
            return await news_dao.get_by_id(guid)

    async def get_by_news_id_news(self, news_id: str) -> NewsModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import NewsDAO

            news_dao = NewsDAO(session=self._session)
            return await news_dao.get_by_news_id(news_id)

    async def get_images_news(self, news: NewsModel) -> List[NewsImageModel]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import NewsDAO

            news_dao = NewsDAO(session=self._session)
            return await news_dao.get_images(news)

    async def get_all_news(self, tag: str, offset: int, limit: int = 100) -> List[NewsModel]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import NewsDAO

            news_dao = NewsDAO(session=self._session)
            return await news_dao.get_all(tag, offset, limit)

    async def bulk_insert_news(self, data: List[NewsCreateSchema]) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import NewsDAO

            news_dao = NewsDAO(session=self._session)
            return await news_dao.bulk_insert(data)

    async def delete_news(self, guid: UUID4) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import NewsDAO

            news_dao = NewsDAO(session=self._session)
            return await news_dao.delete(guid)

    # Room
    async def create_room(self, data: RoomCreateSchema, corps_guid) -> RoomModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import RoomDAO

            room_dao = RoomDAO(session=self._session)
            return await room_dao.create(data, corps_guid)

    async def bulk_insert_room(self, data: List[RoomCreateSchema]) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import RoomDAO

            room_dao = RoomDAO(session=self._session)
            return await room_dao.bulk_insert(data)

    async def get_by_id_room(self, guid: UUID4) -> RoomModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import RoomDAO

            room_dao = RoomDAO(session=self._session)
            return await room_dao.get_by_id(guid)

    async def get_all_room(self) -> List[RoomModel]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import RoomDAO

            room_dao = RoomDAO(session=self._session)
            return await room_dao.get_all()

    async def get_by_number_room(self, number: str) -> RoomModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import RoomDAO

            room_dao = RoomDAO(session=self._session)
            return await room_dao.get_by_number(number)

    async def get_empty_room(
        self, room_filter: RoomFilter, corps: List[str]
    ) -> List[Tuple[str, datetime.time, datetime.time, str]]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import RoomDAO

            room_dao = RoomDAO(session=self._session)
            return await room_dao.get_empty(room_filter, corps)

    async def update_room(self, guid: UUID4, data: RoomCreateSchema) -> RoomModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import RoomDAO

            room_dao = RoomDAO(session=self._session)
            return await room_dao.update(guid, data)

    async def delete_room(self, guid: UUID4) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import RoomDAO

            room_dao = RoomDAO(session=self._session)
            return await room_dao.delete(guid)

    # Start semester
    async def create_start_semester(self, data: StartSemesterCreateSchema) -> StartSemesterModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import StartSemesterDAO

            start_semester_dao = StartSemesterDAO(session=self._session)
            return await start_semester_dao.create(data)

    async def get_start_semester(self) -> StartSemesterModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import StartSemesterDAO

            start_semester_dao = StartSemesterDAO(session=self._session)
            return await start_semester_dao.get()

    async def update_start_semester(self, data: StartSemesterCreateSchema) -> StartSemesterModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import StartSemesterDAO

            start_semester_dao = StartSemesterDAO(session=self._session)
            return await start_semester_dao.update(data)

    # Teacher
    async def create_teacher(self, data: TeacherCreateSchema) -> TeacherModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import TeacherDAO

            teacher_dao = TeacherDAO(session=self._session)
            return await teacher_dao.create(data)

    async def bulk_insert_teacher(self, data: List[TeacherCreateSchema]) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import TeacherDAO

            teacher_dao = TeacherDAO(session=self._session)
            return await teacher_dao.bulk_insert(data)

    async def bulk_insert_trans_teacher(self, data: List[TeacherTranslateLoading]) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import TeacherDAO

            teacher_dao = TeacherDAO(session=self._session)
            return await teacher_dao.bulk_insert_trans(data)

    async def get_by_id_teacher(self, guid: UUID4) -> TeacherModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import TeacherDAO

            teacher_dao = TeacherDAO(session=self._session)
            return await teacher_dao.get_by_id(guid)

    async def get_all_teacher(self, lang: str) -> List[str]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import TeacherDAO

            teacher_dao = TeacherDAO(session=self._session)
            return await teacher_dao.get_all(lang)

    async def get_all_full_teacher(self, lang: str) -> List[str]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import TeacherDAO

            teacher_dao = TeacherDAO(session=self._session)
            return await teacher_dao.get_all_full(lang)

    async def get_all_trans_teacher(
        self, limit: int = -1, offset: int = -1, lang: str = "ru"
    ) -> List[TeacherTranslateModel]:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import TeacherDAO

            teacher_dao = TeacherDAO(session=self._session)
        return await teacher_dao.get_all_trans(limit=limit, offset=offset, lang=lang)

    async def get_by_name_teacher(self, name: str) -> TeacherModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import TeacherDAO

            teacher_dao = TeacherDAO(session=self._session)
            return await teacher_dao.get_by_name(name)

    async def get_unique_teacher(self, data: TeacherCreateSchema) -> TeacherModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import TeacherDAO

            teacher_dao = TeacherDAO(session=self._session)
            return await teacher_dao.get_unique(data)

    async def get_trans_teacher(self, teacher: TeacherModel, lang: str) -> TeacherTranslateModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import TeacherDAO

            teacher_dao = TeacherDAO(session=self._session)
            return await teacher_dao.get_trans(teacher, lang)

    async def update_teacher(self, guid: UUID4, data: TeacherCreateSchema) -> TeacherModel:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import TeacherDAO

            teacher_dao = TeacherDAO(session=self._session)
            return await teacher_dao.update(guid, data)

    async def delete_teacher(self, guid: UUID4) -> None:
        if self._version >= "0.0.1":
            from backend.api.database.dao.v0_0_1 import TeacherDAO

            teacher_dao = TeacherDAO(session=self._session)
            return await teacher_dao.delete(guid)
