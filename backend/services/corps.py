import time

from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.corps import CorpsRepository
from backend.schemas.corps import CorpsCreateSchema, CorpsOutputSchema, CorpsSchema


class CorpsService:
    @staticmethod
    async def create(db: AsyncSession, schemas: CorpsCreateSchema) -> CorpsOutputSchema:
        corps = await CorpsRepository.get_by_name(db, schemas.name)
        if corps is not None:
            raise HTTPException(409, "Корпус уже существует")
        else:
            corps = await CorpsRepository.create(db, schemas)
        return CorpsOutputSchema(**CorpsSchema.from_orm(corps).dict())

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> CorpsOutputSchema:
        corps = await CorpsRepository.get_by_id(db, guid)
        if corps is None:
            raise HTTPException(404, "Корпус не найден")
        return CorpsOutputSchema(**CorpsSchema.from_orm(corps).dict())

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> CorpsOutputSchema:
        corps = await CorpsRepository.get_by_name(db, name)
        if corps is None:
            raise HTTPException(404, "Корпус не найден")
        return CorpsOutputSchema(**CorpsSchema.from_orm(corps).dict())

    @staticmethod
    async def get_all(db: AsyncSession) -> dict[str, list[str]]:
        corps = await CorpsRepository.get_all(db)
        corps.sort()
        return {"corps": corps}

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: CorpsCreateSchema) -> CorpsOutputSchema:
        corps = await CorpsRepository.update(db, guid, schemas)
        if corps is None:
            raise HTTPException(404, "Корпус не найден")
        return CorpsOutputSchema(**CorpsSchema.from_orm(corps).dict())

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await CorpsRepository.delete(db, guid)
        return Response(status_code=204)
