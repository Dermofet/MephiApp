from datetime import date

from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.start_semester import StartSemesterRepository
from backend.schemas.start_semester import StartSemesterCreateSchema, StartSemesterOutputSchema, StartSemesterSchema


class StartSemesterService:
    @staticmethod
    async def create(db: AsyncSession, schemas: StartSemesterCreateSchema) -> StartSemesterOutputSchema:
        start_semester = await StartSemesterRepository.get(db)
        if start_semester is not None:
            raise HTTPException(409, "Дата уже существует")
        else:
            start_semester = await StartSemesterRepository.create(db, schemas)
        return StartSemesterOutputSchema(**StartSemesterSchema.from_orm(start_semester).dict())

    @staticmethod
    async def get(db: AsyncSession) -> StartSemesterOutputSchema:
        start_semester = await StartSemesterRepository.get(db)
        if start_semester is None:
            raise HTTPException(404, "Даты не cуществует")
        return StartSemesterOutputSchema(**StartSemesterSchema.from_orm(start_semester).dict())

    @staticmethod
    async def update(db: AsyncSession, schemas: StartSemesterCreateSchema) -> StartSemesterOutputSchema:
        start_semester = await StartSemesterRepository.update(db, schemas)
        if start_semester is None:
            raise HTTPException(404, "Даты не cуществует")
        return StartSemesterOutputSchema(**StartSemesterSchema.from_orm(start_semester).dict())
