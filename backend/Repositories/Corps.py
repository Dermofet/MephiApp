from datetime import date

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.DataBase.Models.Corps import Corps
from backend.DataBase.Models.Lesson import Lesson
from backend.Schemas.Corps import CorpsCreate, CorpsOutput


class CorpsRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: CorpsCreate) -> Corps:
        corps = Corps(**schemas.dict(exclude_unset=True))
        db.add(corps)
        await db.commit()
        await db.refresh(corps)
        return corps

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> Corps:
        corps = await db.execute(select(Corps).where(Corps.guid == guid).limit(1))
        return corps.scalars()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Corps:
        corps = await db.execute(select(Corps).where(Corps.name == name).limit(1))
        return corps.scalars()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: CorpsCreate) -> Corps:
        corps = await CorpsRepository.get_by_id(db, guid)

        if corps is None:
            HTTPException(status_code=404, detail="Корпус не найден")

        await db.execute(update(Corps).where(Corps.guid == guid).values(**schemas.dict()))
        await db.commit()
        await db.refresh(corps)

        return corps

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(Corps).where(Corps.guid == guid))
        await db.commit()
