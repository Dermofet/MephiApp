from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.Repositories.Corps import CorpsRepository
from backend.Schemas.Corps import Corps, CorpsCreate, CorpsOutput


class CorpsService:
    @staticmethod
    async def create(db: AsyncSession, schemas: CorpsCreate) -> CorpsOutput:
        corps = await CorpsRepository.get_by_name(db, schemas)
        if corps is not None:
            raise HTTPException(409, "Корпус уже существует")
        else:
            corps = await CorpsRepository.create(db, schemas)
        return CorpsOutput(**Corps.from_orm(corps).dict())

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> CorpsOutput:
        corps = await CorpsRepository.get_by_id(db, guid)
        if corps is None:
            raise HTTPException(404, "Корпус не найден")
        return CorpsOutput(**Corps.from_orm(corps).dict())

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> CorpsOutput:
        corps = await CorpsRepository.get_by_name(db, name)
        if corps is None:
            raise HTTPException(404, "Корпус не найден")
        return CorpsOutput(**Corps.from_orm(corps).dict())

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: CorpsCreate) -> CorpsOutput:
        corps = await CorpsRepository.update(db, guid, schemas)
        if corps is None:
            raise HTTPException(404, "Корпус не найден")
        return CorpsOutput(**Corps.from_orm(corps).dict())

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await CorpsRepository.delete(db, guid)
        return Response(status_code=204)
