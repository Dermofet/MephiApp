from typing import List
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.database.models.corps import CorpsModel

from backend.api.schemas.corps import CorpsCreateSchema

class CorpsDAO:
    """
    DAO для работы с корпусами
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    """
    Создание корпуса
    """
    async def create(self, data: CorpsCreateSchema) -> CorpsModel:
        corps = CorpsModel(**data.model_dump())
        self._session.add(corps)
        await self._session.flush()
        await self._session.refresh(corps)
        return corps

    """
    Обновление корпуса
    """
    async def bulk_insert(self, data: List[CorpsCreateSchema]) -> None:
        insert_data = [CorpsModel(**corps.model_dump()) for corps in data]
        self._session.add_all(insert_data)
        await self._session.flush()

    """
    Получение корпуса по id
    """
    async def get_by_id(self, guid: UUID4) -> CorpsModel:
        corps = await self._session.execute(select(CorpsModel).where(CorpsModel.guid == guid).limit(1))
        return corps.scalar()

    """
    Получение корпуса по имени
    """
    async def get_by_name(self, name: str) -> CorpsModel:
        corps = await self._session.execute(select(CorpsModel).where(CorpsModel.name == name).limit(1))
        return corps.scalar()

    """
    Получение всех корпусов
    """
    async def get_all(self) -> List[CorpsModel]:
        corps = await self._session.execute(select(CorpsModel.name).distinct())
        return corps.scalars().all()

    """
    Обновление корпуса
    """
    async def update(self, guid: UUID4, data: CorpsCreateSchema) -> CorpsModel:
        corps = await self.get_by_id(guid)

        if corps is None:
            HTTPException(status_code=404, detail="Корпус не найден")

        await self._session.execute(update(CorpsModel).where(CorpsModel.guid == guid).values(**data.model_dump()))
        await self._session.flush()
        await self._session.refresh(corps)

        return corps

    """
    Удаление корпуса
    """
    async def delete(self, guid: UUID4) -> None:
        await self._session.execute(delete(CorpsModel).where(CorpsModel.guid == guid))
        await self._session.flush()