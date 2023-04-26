import datetime
import time
import uuid
from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import and_, delete, exists, join, not_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.association_tables import AT_lesson_room
from backend.database.models.corps import CorpsModel
from backend.database.models.lesson import LessonModel
from backend.database.models.room import RoomModel
from backend.filters.room import RoomFilter
from backend.repositories.start_semester import StartSemesterRepository
from backend.schemas.room import RoomCreateSchema

weekdays = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}


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
    async def get_empty(db: AsyncSession, room_filter: RoomFilter) -> List[tuple[str, datetime.time, datetime.time]]:
        date = await StartSemesterRepository.get(db)
        week = (room_filter.date_ - date.date).days // 7 + 1
        if week == 2:
            week = [0, 1, 2]
        elif week == 1:
            week = [1, 2]
        else:
            week = [0, 2]

        occupied_rooms = await db.execute(
            select(
                RoomModel.number.label("room_number"),
                LessonModel.time_start.label("lesson_time_start"),
                LessonModel.time_end.label("lesson_time_end"),
            )
            .join(RoomModel.lessons)
            .where(
                and_(
                    RoomModel.corps.has(name=room_filter.corps),
                    LessonModel.day == weekdays[room_filter.date_.weekday()],
                    LessonModel.weeks.in_(week),
                    or_(
                        LessonModel.date_start.is_(None),
                        and_(
                            LessonModel.date_start == room_filter.date_,
                            LessonModel.date_end.is_(None)
                        ),
                        and_(
                            LessonModel.date_start <= room_filter.date_,
                            LessonModel.date_end >= room_filter.date_
                        )
                    ),
                    or_(
                        and_(
                            LessonModel.time_start >= room_filter.time_start,
                            LessonModel.time_start <= room_filter.time_end
                        ),
                        and_(
                            LessonModel.time_end >= room_filter.time_start,
                            LessonModel.time_end <= room_filter.time_end
                        ),
                        and_(
                            LessonModel.time_start < room_filter.time_start,
                            LessonModel.time_end > room_filter.time_end
                        )
                    )
                )
            )
            .distinct().order_by(RoomModel.number, LessonModel.time_start)
        )

        occupied_rooms = occupied_rooms.all()

        occupied_rooms_numbers = [room[0] for room in occupied_rooms]
        full_time_free_rooms = await db.execute(
            select(
                RoomModel.number.label("room_number")
            )
            .where(
                and_(
                    RoomModel.corps.has(name=room_filter.corps),
                    RoomModel.number.notin_(occupied_rooms_numbers)
                )
            )
        )

        full_time_free_rooms = full_time_free_rooms.scalars().unique().all()

        last_room = None
        free_rooms = []
        deltatime = datetime.timedelta(minutes=10)
        for room in occupied_rooms:
            if last_room is None:
                if room[1] > room_filter.time_start and \
                        RoomRepository.sub_time(room[1], room_filter.time_start) > deltatime:
                    free_rooms.append((room[0], room_filter.time_start, room[1]))
                last_room = room
                continue

            if last_room[0] == room[0]:
                if RoomRepository.sub_time(room[1], last_room[2]) > deltatime:
                    free_rooms.append((last_room[0], last_room[2], room[1]))
                last_room = room
                continue

            if last_room[2] < room_filter.time_end and \
                    RoomRepository.sub_time(room_filter.time_end, last_room[2]) > deltatime:
                free_rooms.append((last_room[0], last_room[2], room_filter.time_end))

            if room[1] > room_filter.time_start and \
                    RoomRepository.sub_time(room[1], room_filter.time_start) > deltatime:
                free_rooms.append((room[0], room_filter.time_start, room[1]))
            last_room = room

        for room in full_time_free_rooms:
            free_rooms.append((room, room_filter.time_start, room_filter.time_end))

        return free_rooms

    @staticmethod
    def sub_time(time1: datetime.time, time2: datetime.time) -> datetime.timedelta:
        datetime1 = datetime.datetime.combine(datetime.date.today(), time1)
        datetime2 = datetime.datetime.combine(datetime.date.today(), time2)
        return datetime2 - datetime1

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
