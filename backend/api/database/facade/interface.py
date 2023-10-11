import datetime
from abc import ABC, abstractmethod
from typing import List, Tuple

from pydantic import UUID4, BaseModel

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


class IFacadeDB(ABC):
    
    @abstractmethod
    async def is_alive(self) -> bool:
        ...

    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def refresh(self, model: BaseModel) -> BaseModel:
        ...

    @abstractmethod
    async def rollback(self) -> None:
        ...

    @abstractmethod
    async def create_academic(self, data: AcademicCreateSchema) -> AcademicModel:
        ...

    @abstractmethod
    async def bulk_insert_academic(self, data: List[AcademicCreateSchema]) -> None:
        ...

    @abstractmethod
    async def get_all_academics(self) -> List[AcademicModel]:
        ...

    @abstractmethod
    async def get_by_id_academic(self, guid: UUID4) -> AcademicModel:
        ...

    @abstractmethod
    async def get_by_name_academic(self, name: str) -> AcademicModel:
        ...

    @abstractmethod
    async def update_academic(self, guid: UUID4, data: AcademicCreateSchema) -> AcademicModel:
        ...

    @abstractmethod
    async def delete_academic(self, guid: UUID4) -> None:
        ...

    @abstractmethod
    async def create_corps(self, data: CorpsCreateSchema) -> CorpsModel:
        ...

    @abstractmethod
    async def bulk_insert_corps(self, data: List[CorpsCreateSchema]) -> None:
        ...

    @abstractmethod
    async def get_by_id_corps(self, guid: UUID4) -> CorpsModel:
        ...

    @abstractmethod
    async def get_by_name_corps(self, name: str) -> CorpsModel:
        ...

    @abstractmethod
    async def get_all_corps(self, ) -> List[CorpsModel]:
        ...

    @abstractmethod
    async def update_corps(self, guid: UUID4, data: CorpsCreateSchema) -> CorpsModel:
        ...

    @abstractmethod
    async def delete_corps(self, guid: UUID4) -> None:
        ...

    @abstractmethod
    async def create_group(self, data: GroupCreateSchema, academic_guid: UUID4) -> GroupModel:
        ...

    @abstractmethod
    async def bulk_insert_group(self, data: list) -> None:
        ...

    @abstractmethod
    async def get_by_id_group(self, guid: UUID4) -> GroupModel:
        ...

    @abstractmethod
    async def get_all_group(self) -> List[str]:
        ...

    @abstractmethod
    async def get_by_name_group(self, name: str) -> GroupModel:
        ...

    @abstractmethod
    async def get_academic_group(self, group: GroupModel) -> AcademicModel:
        ...

    @abstractmethod
    async def update_group(self, guid: UUID4, data: GroupCreateSchema) -> GroupModel:
        ...

    @abstractmethod
    async def delete_group(self, guid: UUID4) -> None:
        ...

    @abstractmethod
    async def create_lesson(self, data: LessonCreateSchema) -> LessonModel:
        ...

    @abstractmethod
    async def bulk_insert_lesson(self, data: List[LessonCreateSchema]) -> None:
        ...

    @abstractmethod
    async def get_all_lesson(self, limit: int, offset: int) -> List[LessonModel]:
        ...

    @abstractmethod
    async def get_by_id_lesson(self, guid: UUID4) -> LessonModel:
        ...

    @abstractmethod
    async def get_unique_lesson(self, data: LessonCreateSchema) -> LessonModel:
        ...

    @abstractmethod
    async def get_lesson_lesson(self, data: LessonCreateSchema) -> LessonModel:
        ...

    @abstractmethod
    async def get_id_lesson(self, data: LessonCreateSchema) -> UUID4:
        ...

    @abstractmethod
    async def get_trans_lesson(self, lesson: LessonModel, lang: str) -> LessonTranslateModel:
        ...

    @abstractmethod
    async def get_teachers_lesson(self, lesson: LessonModel, lang: str) -> List[Tuple[TeacherModel, TeacherTranslateModel]]:
        ...

    @abstractmethod
    async def get_groups_lesson(self, lesson: LessonModel) -> List[GroupModel]:
        ...

    @abstractmethod
    async def get_rooms_lesson(self, lesson: LessonModel) -> List[RoomModel]:
        ...

    @abstractmethod
    async def get_by_group_lesson(self, group: str, lang: str, date_: datetime.date = datetime.date.today()) -> List[
        LessonModel]:
        ...

    @abstractmethod
    async def get_by_teacher_lesson(self, teacher: str, lang: str, date_: datetime.date = datetime.date.today()) -> \
            List[LessonModel]:
        ...

    @abstractmethod
    async def update_lesson(self, guid: UUID4, data: LessonCreateSchema) -> LessonModel:
        ...

    @abstractmethod
    async def update_translate_lesson(self, data: LessonCreateSchema, guid: str) -> LessonModel:
        ...

    @abstractmethod
    async def delete_lesson(self, guid: UUID4) -> None:
        ...

    @abstractmethod
    async def get_by_id_news(self, guid: UUID4) -> NewsModel:
        ...

    @abstractmethod
    async def get_images_news(self, news: NewsModel) -> List[NewsImageModel]:
        ...

    @abstractmethod
    async def get_by_news_id_news(self, news_id: str) -> NewsModel:
        ...

    @abstractmethod
    async def get_all_news(self, tag: str, offset: int, limit: int = 100) -> List[NewsModel]:
        ...

    @abstractmethod
    async def bulk_insert_news(self, data: List[NewsCreateSchema]) -> None:
        ...

    @abstractmethod
    async def delete_news(self, guid: UUID4) -> None:
        ...

    @abstractmethod
    async def create_room(self, data: RoomCreateSchema, corps_guid) -> RoomModel:
        ...

    @abstractmethod
    async def bulk_insert_room(self, data: List[RoomCreateSchema]) -> None:
        ...

    @abstractmethod
    async def get_by_id_room(self, guid: UUID4) -> RoomModel:
        ...

    @abstractmethod
    async def get_all_room(self, ) -> List[RoomModel]:
        ...

    @abstractmethod
    async def get_by_number_room(self, number: str) -> RoomModel:
        ...

    @abstractmethod
    async def get_empty_room(self, room_filter: RoomFilter, corps: list[str]) -> List[
        tuple[str, datetime.time, datetime.time, str]]:
        ...

    @abstractmethod
    async def update_room(self, guid: UUID4, data: RoomCreateSchema) -> RoomModel:
        ...

    @abstractmethod
    async def delete_room(self, guid: UUID4) -> None:
        ...

    @abstractmethod
    async def create_start_semester(self, data: StartSemesterCreateSchema) -> StartSemesterModel:
        ...

    @abstractmethod
    async def get_start_semester(self, ) -> StartSemesterModel:
        ...

    @abstractmethod
    async def update_start_semester(self, data: StartSemesterCreateSchema) -> StartSemesterModel:
        ...

    @abstractmethod
    async def create_teacher(self, data: TeacherCreateSchema) -> TeacherModel:
        ...

    @abstractmethod
    async def bulk_insert_teacher(self, data: List[TeacherCreateSchema]) -> None:
        ...

    @abstractmethod
    async def get_by_id_teacher(self, guid: UUID4) -> TeacherModel:
        ...

    @abstractmethod
    async def get_all_teacher(self, lang: str) -> List[str]:
        ...

    @abstractmethod
    async def get_all_full_teacher(self, lang: str) -> List[str]:
        ...    

    @abstractmethod
    async def get_by_name_teacher(self, name: str) -> TeacherModel:
        ...

    @abstractmethod
    async def get_unique_teacher(self, data: TeacherCreateSchema) -> TeacherModel:
        ...

    @abstractmethod
    async def get_trans_teacher(self, teacher: TeacherModel, lang: str) -> TeacherTranslateModel:
        ...

    @abstractmethod
    async def update_teacher(self, guid: UUID4, data: TeacherCreateSchema) -> TeacherModel:
        ...

    @abstractmethod
    async def delete_teacher(self, guid: UUID4) -> None:
        ...
