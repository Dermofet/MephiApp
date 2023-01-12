from datetime import date
from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.DataBase.Models.Lesson import Lesson
from backend.DataBase.Models.Room import Room
from backend.Filters.Room import RoomFilter
from backend.Schemas.Room import RoomCreate, RoomOutput


class RoomRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: RoomCreate) -> Room:
        room = Room(**schemas.dict(exclude_unset=True))
        db.add(room)
        await db.commit()
        await db.refresh(room)
        return room

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> Room:
        room = await db.execute(select(Room).where(Room.guid == guid).limit(1))
        if len(room.scalars().all()) > 0:
            return room.scalars().all()[0]
        return None

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Room]:
        rooms = await db.execute(select(Room))
        return rooms.scalars().unique().all()

    @staticmethod
    async def get_by_number(db: AsyncSession, number: str) -> Room:
        room = await db.execute(select(Room).where(Room.number == number).limit(1))
        if len(room.scalars().all()) > 0:
            return room.scalars().all()[0]
        return None

    @staticmethod
    async def get_empty(db: AsyncSession, room_filter: RoomFilter) -> List[Room]:
        rooms = await db.execute(room_filter.filter(select(Room).outerjoin(Lesson).outerjoin(Corps)))

        # rooms = await db.execute(
        #     select(Room).join(Lesson).where(Lesson.time_start == time_start and
        #                                     Lesson.time_end == time_end and
        #                                     Lesson.weeks == week and
        #                                     ((Lesson.date_start is not None and Lesson.date_start < _date) or
        #                                      (Lesson.date_end is not None and Lesson.date_end < _date) or
        #                                      True) and
        #                                     Room.guid != Lesson.room_guid))
        return rooms.scalars().unique().all()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: RoomCreate) -> Room:
        room = await RoomRepository.get_by_id(db, guid)

        if room is None:
            HTTPException(status_code=404, detail="Кабинет не найден")

        room = await db.execute(update(Room).where(Room.guid == guid).values(**schemas.dict()))
        await db.commit()
        await db.refresh(room)
        return room

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(Room).where(Room.guid == guid))
        await db.commit()
