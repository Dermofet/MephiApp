from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.Repositories.Academic import AcademicRepository
from backend.Schemas.Academic import AcademicCreate, AcademicOutput


class AcademicService:
    @staticmethod
    async def create(db: AsyncSession, schemas: AcademicCreate) -> AcademicOutput:
        academic = await AcademicRepository.get_by_name(db, schemas)
        if academic is not None:
            raise HTTPException(409, "Ученое звание уже существует")
        else:
            academic = await AcademicRepository.create(db, schemas)
        return AcademicOutput.from_orm(academic)

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> AcademicOutput:
        academic = await AcademicRepository.get_by_id(db, guid)
        if academic is None:
            raise HTTPException(404, "Ученое звание не найдено")
        return AcademicOutput.from_orm(academic)

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> AcademicOutput:
        academic = await AcademicRepository.get_by_name(db, name)
        if academic is None:
            raise HTTPException(404, "Ученое звание не найдено")
        return AcademicOutput.from_orm(academic)

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: AcademicCreate) -> AcademicOutput:
        academic = await AcademicRepository.update(db, guid, schemas)
        if academic is None:
            raise HTTPException(404, "Ученое звание не найдено")
        return AcademicOutput.from_orm(academic)

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await AcademicRepository.delete(db, guid)
        return Response(status_code=204)
