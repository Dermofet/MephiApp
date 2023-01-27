from datetime import date

from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.Filters.Room import RoomFilter
from backend.Repositories.Room import RoomRepository
from backend.Schemas.Room import Room, RoomCreate, RoomOutput


class RoomService:
    @staticmethod
    async def create(db: AsyncSession, schemas: RoomCreate) -> RoomOutput:
        room = await RoomRepository.get_by_name(db, schemas)
        if room is not None:
            raise HTTPException(409, "Аудитория уже существует")
        else:
            room = await RoomRepository.create(db, schemas)
        return RoomOutput(**Room.from_orm(room).dict())

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> RoomOutput:
        room = await RoomRepository.get_by_id(db, guid)
        if room is None:
            raise HTTPException(404, "Аудитория не найдена")
        return RoomOutput(**Room.from_orm(room).dict())

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> RoomOutput:
        room = await RoomRepository.get_by_name(db, name)
        if room is None:
            raise HTTPException(404, "Аудитория не найдена")
        return RoomOutput(**Room.from_orm(room).dict())

    @staticmethod
    async def get_all(db: AsyncSession) -> list[str]:
        rooms = await RoomRepository.get_all(db)
        if rooms is None:
            raise HTTPException(404, "Аудитория не найдена")
        return [RoomOutput(**Room.from_orm(room).dict()) for room in rooms]

    @staticmethod
    async def get_empty(db: AsyncSession, room_filter: RoomFilter) -> list[str]:
        room_filter.week = room_filter.week % 2
        rooms = await RoomRepository.get_empty(db, room_filter)
        if rooms is None:
            raise HTTPException(404, "Аудитория не найдена")
        return [RoomOutput(**Room.from_orm(room).dict()) for room in rooms]

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: RoomCreate) -> RoomOutput:
        room = await RoomRepository.update(db, guid, schemas)
        if room is None:
            raise HTTPException(404, "Аудитория не найдена")
        return RoomOutput(**Room.from_orm(room).dict())

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await RoomRepository.delete(db, guid)
        return Response(status_code=204)
