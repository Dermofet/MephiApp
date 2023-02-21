from datetime import date

from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.filters.room import RoomFilter
from backend.repositories.corps import CorpsRepository
from backend.repositories.room import RoomRepository
from backend.schemas.corps import CorpsCreateSchema
from backend.schemas.room import RoomCreateSchema, RoomOutputSchema, RoomSchema


class RoomService:
    @staticmethod
    async def create(db: AsyncSession, schemas: RoomCreateSchema) -> RoomOutputSchema:
        room = await RoomRepository.get_by_number(db, schemas.number)
        if room is not None:
            raise HTTPException(409, "Аудитория уже существует")
        else:
            corps = await CorpsRepository.get_by_name(db, name=schemas.corps)
            if corps is None:
                raise HTTPException(404, "Корпус, в котором находится аудитория, не найден")
            room = await RoomRepository.create(db, schemas, corps_guid=corps.guid)
        return RoomOutputSchema(**RoomSchema.from_orm(room).dict())

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> RoomOutputSchema:
        room = await RoomRepository.get_by_id(db, guid)
        if room is None:
            raise HTTPException(404, "Аудитория не найдена")
        return RoomOutputSchema(**RoomSchema.from_orm(room).dict())

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> RoomOutputSchema:
        room = await RoomRepository.get_by_name(db, name)
        if room is None:
            raise HTTPException(404, "Аудитория не найдена")
        return RoomOutputSchema(**RoomSchema.from_orm(room).dict())

    @staticmethod
    async def get_all(db: AsyncSession) -> list[str]:
        rooms = await RoomRepository.get_all(db)
        # if not rooms:
        #     raise HTTPException(404, "Аудитории не найдены")
        return [RoomOutputSchema(**RoomSchema.from_orm(room).dict()) for room in rooms]

    @staticmethod
    async def get_empty(db: AsyncSession, room_filter: RoomFilter) -> dict[str, list[dict]]:
        rooms = await RoomRepository.get_empty(db, room_filter)
        # if rooms is None:
        #     raise HTTPException(404, "Аудитории не найдены")
        return {"rooms": [{"name": RoomOutputSchema(**RoomSchema.from_orm(room).dict()).number,
                           "floor": None} for room in rooms]}

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: RoomCreateSchema) -> RoomOutputSchema:
        room = await RoomRepository.update(db, guid, schemas)
        if room is None:
            raise HTTPException(404, "Аудитория не найдена")
        return RoomOutputSchema(**RoomSchema.from_orm(room).dict())

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await RoomRepository.delete(db, guid)
        return Response(status_code=204)
