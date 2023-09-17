from typing import List
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.database.models.teacher import TeacherModel
from backend.api.database.models.teacher_translate import TeacherTranslateModel
from backend.api.schemas.teacher import TeacherCreateSchema

class TeacherDAO:
    """
    DAO для работы с преподавателями
    """

    _session: AsyncSession

    def __init__(self, session: AsyncSession):
        self._session = session

    """
    Создание преподавателя
    """
    async def create(self, data: TeacherCreateSchema) -> TeacherModel:
        teacher = TeacherModel(**data.model_dump())

        self._session.add(teacher)
        await self._session.flush()
        await self._session.refresh(teacher)

        return teacher

    """
    Получение преподавателя по id
    """
    async def bulk_insert(self, data: List[TeacherCreateSchema]) -> None:
        db_teachers = []
        for teacher in data:
            t = TeacherModel(url=teacher.url, alt_url=teacher.alt_url)
            t.trans.add(TeacherTranslateModel(lang=teacher.lang, name=teacher.name, fullname=teacher.fullname))
            db_teachers.append(t)
        self._session.add_all(db_teachers)
        await self._session.flush()

    """
    Получение преподавателя по имени
    """
    async def get_by_id(self, guid: UUID4) -> TeacherModel:
        teacher = await self._session.execute(select(TeacherModel).where(TeacherModel.guid == guid).limit(1))
        return teacher.scalar()

    """
    Получение всех преподавателей
    """
    async def get_all(self, lang: str) -> List[str]:
        teachers = await self._session.execute(
            select(TeacherTranslateModel.name)
            .where(TeacherTranslateModel.lang == lang)
        )
        return teachers.scalars().unique().all()

    """
    Получение преподавателя по имени
    """
    # TODO сделать 1 запрос из 2
    async def get_by_name(self, name: str) -> TeacherModel:
        trans = await self._session.execute(
            select(TeacherTranslateModel)
            .where(TeacherTranslateModel.name == name)
            .limit(1)
        )

        trans = trans.scalar()
        if trans is None:
            return None
        
        teacher = await self._session.execute(
            select(TeacherModel)
            .where(TeacherModel.guid == trans.teacher_guid)
            .limit(1)
        )
        return teacher.scalar()

    async def get_trans(self, teacher: TeacherModel, lang: str = None) -> TeacherTranslateModel:
        trans = await self._session.execute(teacher.trans.select().where(TeacherTranslateModel.lang == lang).limit(1))
        return trans.scalar()
    
    async def get_all_trans(self, teacher: TeacherModel) -> List[TeacherTranslateModel]:
        teachers = await self._session.execute(select(TeacherTranslateModel).where(TeacherTranslateModel.teacher_guid == teacher.guid))
        return teachers.scalars().all()

    """
    Получение уникального преподавателя
    """
    async def get_unique(self, data: TeacherCreateSchema) -> TeacherModel:
        teacher = await self._session.execute(
            select(TeacherModel)
            .join(TeacherTranslateModel, TeacherTranslateModel.guid == TeacherModel.guid)
            .where(
                TeacherModel.name == data.name and
                TeacherModel.lang == data.lang and
                TeacherModel.fullname == data.fullname
            )
            .limit(1)
        )
        return teacher.scalar()

    """
    Обновление преподавателя
    """
    async def update(self, guid: UUID4, data: TeacherCreateSchema) -> TeacherModel:
        teacher = await self.get_by_name(data.name)

        if teacher is None:
            raise HTTPException(404, "Преподавателя не существует")

        await self._session.execute(
            update(TeacherModel)
            .where(TeacherModel.guid == guid)
            .values(url=data.url, alt_url=data.alt_url)
        )
        await self._session.execute(
            update(TeacherTranslateModel)
            .where(TeacherTranslateModel.teacher_guid == guid, TeacherTranslateModel.lang == data.lang)
            .values(name=data.name, fullname=data.fullname)
        )

        await self._session.flush()
        await self._session.refresh(teacher)

        return teacher

    """
    Удаление преподавателя
    """
    async def delete(self, guid: UUID4) -> None:
        await self._session.execute(delete(TeacherModel).where(TeacherModel.guid == guid))
        await self._session.flush()