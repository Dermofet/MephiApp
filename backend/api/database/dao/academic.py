from typing import List
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from backend.api.database.models.academic import AcademicModel

from backend.api.schemas.academic import AcademicCreateSchema

class AcademicDAO:
    """
    DAO для работы с учеными званиями
    """

    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    """
    Создание ученого звания
    """
    async def create(self, data: AcademicCreateSchema) -> AcademicModel:
        academic = AcademicModel(**data.model_dump())
        self.session.add(academic)
        await self.session.flush()
        await self.session.refresh(academic)
        return academic

    """
    Получение ученого звания по id
    """
    async def bulk_insert(self, data: List[AcademicCreateSchema]) -> None:
        insert_data = [AcademicModel(**academic.model_dump()) for academic in data]
        self.session.add_all(insert_data)
        await self.session.flush()

    """
    Получение ученого звания по имени
    """
    async def get_by_id(self, guid: UUID4) -> AcademicModel:
        academic = await self.session.execute(select(AcademicModel). where(AcademicModel.guid == guid).limit(1))
        return academic.scalar()

    """
    Получение ученого звания по имени
    """
    async def get_by_name(self, name: str) -> AcademicModel:
        academic = await self.session.execute(select(AcademicModel).where(AcademicModel.name == name).limit(1))
        return academic.scalar()
    
    """
    Получение всех ученых званий
    """
    async def get_all(self) -> List[AcademicModel]:
        academic = await self.session.execute(select(AcademicModel))
        return academic.scalars().all()

    """
    Обновление ученого звания
    """
    async def update(self, guid: UUID4, data: AcademicCreateSchema) -> AcademicModel:
        academic = await self.get_by_id(guid)

        if academic is None:
            HTTPException(status_code=404, detail="Ученое звание не найден")

        await self.session.execute(update(AcademicModel).where(AcademicModel.guid == guid).values(**data.model_dump()))
        await self.session.flush()
        await self.session.refresh(academic)

        return academic

    """
    Удаление ученого звания
    """
    async def delete(self, guid: UUID4) -> None:
        await self.session.execute(delete(AcademicModel).where(AcademicModel.guid == guid))
        await self.session.flush()