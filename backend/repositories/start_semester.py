from fastapi import HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.start_semester import StartSemesterModel
from backend.schemas.start_semester import StartSemesterCreateSchema


class StartSemesterRepository:
    @staticmethod
    async def create(db: AsyncSession, schema: StartSemesterCreateSchema) -> StartSemesterModel:
        start_semester = StartSemesterModel(**schema.dict())
        db.add(start_semester)
        await db.commit()
        await db.refresh(start_semester)
        return start_semester

    @staticmethod
    async def get(db: AsyncSession) -> StartSemesterModel:
        start_semester = await db.execute(
            select(StartSemesterModel).limit(1)
        )
        return start_semester.scalar()

    @staticmethod
    async def update(db: AsyncSession, schema: StartSemesterCreateSchema) -> StartSemesterModel:
        start_semester = await StartSemesterRepository.get(db)

        if start_semester is None:
            raise HTTPException(404, "Даты не существует")

        await db.execute(
            update(StartSemesterModel)
            .where(StartSemesterModel.guid == start_semester.guid)
            .values(**schema.dict())
        )
        await db.commit()
        await db.refresh(start_semester)
        return start_semester
