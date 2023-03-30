from datetime import date

from api.backend.database.models.corps import CorpsModel
from api.backend.database.models.lesson import LessonModel
from api.backend.schemas.corps import CorpsCreateSchema, CorpsOutputSchema
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class CorpsRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: CorpsCreateSchema) -> CorpsModel:
        corps = CorpsModel(**schemas.dict(exclude_unset=True))
        db.add(corps)
        await db.commit()
        await db.refresh(corps)
        return corps

    @staticmethod
    async def bulk_insert(db: AsyncSession, data: list) -> None:
        await db.execute(insert(CorpsModel).values(data))

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> CorpsModel:
        corps = await db.execute(select(CorpsModel).where(CorpsModel.guid == guid).limit(1))
        return corps.scalar()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> CorpsModel:
        corps = await db.execute(select(CorpsModel).where(CorpsModel.name == name).limit(1))
        return corps.scalar()

    @staticmethod
    async def get_all(db: AsyncSession) -> list[CorpsModel]:
        corps = await db.execute(select(CorpsModel.name).distinct())
        return corps.scalars().all()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: CorpsCreateSchema) -> CorpsModel:
        corps = await CorpsRepository.get_by_id(db, guid)

        if corps is None:
            HTTPException(status_code=404, detail="Корпус не найден")

        await db.execute(update(CorpsModel).where(CorpsModel.guid == guid).values(**schemas.dict()))
        await db.commit()
        await db.refresh(corps)

        return corps

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(CorpsModel).where(CorpsModel.guid == guid))
        await db.commit()
