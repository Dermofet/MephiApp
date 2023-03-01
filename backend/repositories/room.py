import time
from datetime import date
from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import and_, delete, exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from backend.database.models.association_tables import AT_lesson_room
from backend.database.models.corps import CorpsModel
from backend.database.models.group import GroupModel
from backend.database.models.lesson import LessonModel
from backend.database.models.room import RoomModel
from backend.filters.room import RoomFilter
from backend.schemas.room import RoomCreateSchema, RoomOutputSchema


class RoomRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: RoomCreateSchema, corps_guid) -> RoomModel:
        room = RoomModel(number=schemas.number, corps_guid=corps_guid)
        db.add(room)
        await db.commit()
        await db.refresh(room)
        return room

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> RoomModel:
        room = await db.execute(select(RoomModel).where(RoomModel.guid == guid).limit(1))
        return room.scalar()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[RoomModel]:
        rooms = await db.execute(select(RoomModel))
        return rooms.scalars().unique().all()

    @staticmethod
    async def get_by_number(db: AsyncSession, number: str) -> RoomModel:
        room = await db.execute(select(RoomModel).where(RoomModel.number == number).limit(1))
        return room.scalar()

    @staticmethod
    async def get_empty(db: AsyncSession, room_filter: RoomFilter) -> List[RoomModel]:
        _ = time.time()
        rooms = await db.execute(select(RoomModel.number)
                                 .join(AT_lesson_room,
                                       AT_lesson_room.c.room_guid == RoomModel.guid)
                                 .join(LessonModel,
                                       LessonModel.guid == AT_lesson_room.c.lesson_guid)
                                 .join(CorpsModel,
                                       CorpsModel.guid == RoomModel.corps_guid)
                                 .where((LessonModel.time_start >= room_filter.time_start) &
                                        (LessonModel.time_end <= room_filter.time_end) &
                                        (CorpsModel.name == room_filter.corps) &
                                        (
                                                LessonModel.date_start.is_(None) |
                                                exists().where(
                                                    (LessonModel.date_start <= room_filter.date) &
                                                    (room_filter.date <= LessonModel.date_end)
                                                )
                                        )
                                        )
                                 )

        print(f'Time: {time.time() - _}')
        return rooms.scalars().unique().all()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: RoomCreateSchema) -> RoomModel:
        room = await RoomRepository.get_by_id(db, guid)

        if room is None:
            HTTPException(status_code=404, detail="Кабинет не найден")

        room = await db.execute(update(RoomModel).where(RoomModel.guid == guid).values(**schemas.dict()))
        await db.commit()
        await db.refresh(room)
        return room

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(RoomModel).where(RoomModel.guid == guid))
        await db.commit()
