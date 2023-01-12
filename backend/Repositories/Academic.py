from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.DataBase.Models.Academic import Academic
from backend.Schemas.Academic import AcademicCreate, AcademicOutput


class AcademicRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: AcademicCreate) -> Academic:
        academic = Academic(**schemas.dict(exclude_unset=True))
        db.add(academic)
        await db.commit()
        await db.refresh(academic)
        return academic

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> Academic:
        academic = await db.execute(select(Academic).where(Academic.guid == guid).limit(1))
        if len(academic.scalars().all()) > 0:
            return academic.scalars().all()[0]
        return None

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Academic:
        academic = await db.execute(select(Academic).where(Academic.name == name).limit(1))
        if len(academic.scalars().all()) > 0:
            return academic.scalars().all()[0]
        return None

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: AcademicCreate) -> Academic:
        academic = await AcademicRepository.get_by_id(db, guid)

        if academic is None:
            HTTPException(status_code=404, detail="Ученое звание не найден")

        await db.execute(update(Academic).where(Academic.guid == guid).values(**schemas.dict()))
        await db.commit()
        await db.refresh(academic)

        return academic

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(Academic).where(Academic.guid == guid))
        await db.commit()
