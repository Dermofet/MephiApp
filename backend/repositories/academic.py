from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.academic import AcademicModel
from backend.schemas.academic import AcademicCreateSchema


class AcademicRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: AcademicCreateSchema) -> AcademicModel:
        academic = AcademicModel(**schemas.dict(exclude_unset=True))
        db.add(academic)
        await db.commit()
        await db.refresh(academic)
        return academic

    @staticmethod
    async def bulk_insert(db: AsyncSession, data: list) -> None:
        await db.execute(insert(AcademicModel).values(data))

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> AcademicModel:
        academic = await db.execute(select(AcademicModel).where(AcademicModel.guid == guid).limit(1))
        return academic.scalar()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> AcademicModel:
        academic = await db.execute(select(AcademicModel).where(AcademicModel.name == name).limit(1))
        return academic.scalar()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: AcademicCreateSchema) -> AcademicModel:
        academic = await AcademicRepository.get_by_id(db, guid)

        if academic is None:
            HTTPException(status_code=404, detail="Ученое звание не найден")

        await db.execute(update(AcademicModel).where(AcademicModel.guid == guid).values(**schemas.dict()))
        await db.commit()
        await db.refresh(academic)

        return academic

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(AcademicModel).where(AcademicModel.guid == guid))
        await db.commit()
