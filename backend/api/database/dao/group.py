from typing import List
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.database.models.academic import AcademicModel
from backend.api.database.models.group import GroupModel

from backend.api.schemas.group import GroupCreateSchema

class GroupDAO:
    """
    DAO для работы с группами
    """

    _session: AsyncSession

    def __init__(self, session: AsyncSession):
        self._session = session
    
    """
    Создание группы
    """
    async def create(self, data: GroupCreateSchema, academic_guid: UUID4) -> GroupModel:
        group = GroupModel(name=data.name, course=data.course, academic_guid=academic_guid)
        self._session.add(group)
        await self._session.flush()
        await self._session.refresh(group)
        return group

    """
    Массовое создание групп
    """
    async def bulk_insert(self, data: List[GroupCreateSchema]) -> None:
        academics_models = await self._session.execute(select(AcademicModel))
        academics_models = academics_models.scalars().all()
        academics = {academic.name: academic.guid for academic in academics_models}

        insert_data = [
            GroupModel(
                name=group.name,
                course=group.course,
                academic_guid=academics[group.academic]
            ) 
            for group in data
        ]
        self._session.add_all(insert_data)
        await self._session.flush()

    """
    Получение группы по id
    """
    async def get_by_id(self, guid: UUID4) -> GroupModel:
        group = await self._session.execute(select(GroupModel).where(GroupModel.guid == guid).limit(1))
        return group.scalar()

    """
    Получение всех групп
    """
    async def get_all(self) -> List[str]:
        groups = await self._session.execute(select(GroupModel.name))
        return groups.scalars().unique().all()

    """
    Получение группы по названию
    """
    async def get_by_name(self, name: str) -> GroupModel:
        group = await self._session.execute(select(GroupModel).where(GroupModel.name == name).limit(1))
        return group.scalar()

    async def get_academic(self, group: GroupModel) -> AcademicModel:
        academic = await self._session.execute(select(AcademicModel).where(AcademicModel.guid == group.academic_guid).limit(1))
        return academic.scalar()

    """
    Обновление группы
    """
    async def update(self, guid: UUID4, data: GroupCreateSchema) -> GroupModel:
        group = await self._session.get_by_id(self._session, guid)

        if group is None:
            HTTPException(status_code=404, detail="Группа не найдена")

        group = await self._session.execute(update(GroupModel).where(GroupModel.guid == guid).values(**data.model_dump()))
        await self._session.flush()
        await self._session.refresh(group)
        return group

    """
    Удаление группы
    """
    async def delete(self, guid: UUID4) -> None:
        await self._session.execute(delete(GroupModel).where(GroupModel.guid == guid))
        await self._session.flush()
