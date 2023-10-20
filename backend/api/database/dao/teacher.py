from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.database.models.teacher import TeacherModel
from backend.api.database.models.teacher_translate import TeacherTranslateModel
from backend.api.schemas.teacher import TeacherCreateSchema
from backend.api.schemas.teacher_translate import TeacherTranslateCreateSchema


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
        db_teachers = [
            TeacherModel(
                url=teacher.url,
                alt_url=teacher.alt_url,
                trans=[
                    TeacherTranslateModel(lang=trans.lang, name=trans.name, fullname=trans.fullname)
                    for trans in teacher.trans
                ],
            )
            for teacher in data
        ]
        self._session.add_all(db_teachers)
        await self._session.flush()

    async def bulk_insert_trans(self, data: List[TeacherTranslateCreateSchema]) -> None:
        db_trans = [
            TeacherTranslateModel(
                name=trans.name, fullname=trans.fullname, lang=trans.lang, teacher_guid=trans.teacher_guid
            )
            for trans in data
        ]
        self._session.add_all(db_trans)
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
            select(TeacherTranslateModel.name).where(TeacherTranslateModel.lang == lang)
        )
        return teachers.scalars().unique().all()

    async def get_all_full(self, lang: str) -> List[str]:
        teachers = await self._session.execute(
            select(TeacherModel)
            .join(TeacherTranslateModel, TeacherTranslateModel.teacher_guid == TeacherModel.guid)
            .where(TeacherTranslateModel.lang == lang)
        )
        return teachers.scalars().unique().all()

    async def get_all_trans(self, limit: int = -1, offset: int = -1, lang: str = "ru") -> List[TeacherTranslateModel]:
        query = select(TeacherTranslateModel).where(TeacherTranslateModel.lang == lang)

        if offset != -1:
            query = query.offset(offset)
        if limit != -1:
            query = query.limit(limit)

        trans = await self._session.execute(query)
        return trans.scalars().unique().all()

    """
    Получение преподавателя по имени
    """

    # TODO сделать 1 запрос из 2
    async def get_by_name(self, name: str) -> TeacherModel:
        teacher = await self._session.execute(
            select(TeacherModel)
            .join(TeacherTranslateModel, TeacherTranslateModel.teacher_guid == TeacherModel.guid)
            .where(TeacherTranslateModel.name == name)
            .limit(1)
        )
        return teacher.scalar()

    async def get_trans(self, teacher: TeacherModel, lang: str = None) -> TeacherTranslateModel:
        trans = await self._session.execute(
            select(TeacherTranslateModel)
            .where(TeacherTranslateModel.teacher_guid == teacher.guid, TeacherTranslateModel.lang == lang)
            .limit(1)
        )
        return trans.scalar()

    async def get_all_trans(self, limit: int = -1, offset: int = -1, lang: str = "ru") -> List[TeacherTranslateModel]:
        query = select(TeacherTranslateModel).where(TeacherTranslateModel.lang == lang)
        if offset != -1:
            query = query.offset(offset)
        if limit != -1:
            query = query.limit(limit)

        trans = await self._session.execute(query)
        return trans.scalars().all()

    """
    Получение уникального преподавателя
    """

    async def get_unique(self, data: TeacherCreateSchema) -> TeacherModel:
        teacher = await self._session.execute(
            select(TeacherModel)
            .join(TeacherTranslateModel, TeacherTranslateModel.guid == TeacherModel.guid)
            .where(
                TeacherModel.name == data.name
                and TeacherModel.lang == data.lang
                and TeacherModel.fullname == data.fullname
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
            update(TeacherModel).where(TeacherModel.guid == guid).values(url=data.url, alt_url=data.alt_url)
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
