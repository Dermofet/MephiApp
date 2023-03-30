from api.backend.repositories.academic import AcademicRepository
from api.backend.schemas.academic import AcademicCreateSchema, AcademicOutputSchema, AcademicSchema
from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession


class AcademicService:
    @staticmethod
    async def create(db: AsyncSession, schemas: AcademicCreateSchema) -> AcademicOutputSchema:
        academic = await AcademicRepository.get_by_name(db, schemas.name)
        if academic is not None:
            raise HTTPException(409, "Ученое звание уже существует")
        else:
            academic = await AcademicRepository.create(db, schemas)
        return AcademicOutputSchema(**AcademicSchema.from_orm(academic).dict())

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> AcademicOutputSchema:
        academic = await AcademicRepository.get_by_id(db, guid)
        if academic is None:
            raise HTTPException(404, "Ученое звание не найдено")
        return AcademicOutputSchema(**AcademicSchema.from_orm(academic).dict())

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> AcademicOutputSchema:
        academic = await AcademicRepository.get_by_name(db, name)
        if academic is None:
            raise HTTPException(404, "Ученое звание не найдено")
        return AcademicOutputSchema(**AcademicSchema.from_orm(academic).dict())

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: AcademicCreateSchema) -> AcademicOutputSchema:
        academic = await AcademicRepository.update(db, guid, schemas)
        if academic is None:
            raise HTTPException(404, "Ученое звание не найдено")
        return AcademicOutputSchema(**AcademicSchema.from_orm(academic).dict())

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await AcademicRepository.delete(db, guid)
        return Response(status_code=204)
