import datetime
import os
import time
import uuid
from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import and_, delete, exists, join, not_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.database.models.lesson import LessonModel
from backend.database.models.association_tables import AT_lesson_room
from backend.database.models.corps import CorpsModel
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
    async def get_empty(db: AsyncSession, room_filter: RoomFilter, corps: list[str]) \
            -> List[tuple[str, datetime.time, datetime.time, str]]:
        date = await StartSemesterRepository.get(db)

        if date is None:
            raise HTTPException(409, "Даты начала семестра нет")

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
                CorpsModel.name.label("corps_name")
            )
            .join(RoomModel.lessons)
            .join(RoomModel.corps)
            .where(
                and_(
                    CorpsModel.name.in_(corps),
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

        occupied_rooms_numbers = (room[0] for room in occupied_rooms)
        full_time_free_rooms = await db.execute(
            select(
                RoomModel.number.label("room_number"),
                CorpsModel.name.label("corps_name")
            )
            .join(RoomModel.corps)
            .where(
                and_(
                    CorpsModel.name.in_(corps),
                    RoomModel.number.notin_(occupied_rooms_numbers)
                )
            )
        )

        full_time_free_rooms = full_time_free_rooms.all()

        last_room = None
        free_rooms = []
        deltatime = datetime.timedelta(minutes=10)
        for room in occupied_rooms:
            if last_room is None:
                if room[1] > room_filter.time_start and \
                        RoomRepository.sub_time(room[1], room_filter.time_start) > deltatime:
                    free_rooms.append((room[0], room_filter.time_start, room[1], room[3]))
                last_room = room
                continue

            if last_room[0] == room[0]:
                if RoomRepository.sub_time(last_room[2], room[1]) > deltatime:
                    free_rooms.append((last_room[0], last_room[2], room[1], last_room[3]))
                last_room = room
                continue

            if last_room[2] < room_filter.time_end and \
                    RoomRepository.sub_time(last_room[2], room_filter.time_end) > deltatime:
                free_rooms.append((last_room[0], last_room[2], room_filter.time_end, last_room[3]))

            if room[1] > room_filter.time_start and \
                    RoomRepository.sub_time(room[1], room_filter.time_start) > deltatime:
                free_rooms.append((room[0], room_filter.time_start, room[1], room[3]))
            last_room = room

        for room in full_time_free_rooms:
            free_rooms.append((room[0], room_filter.time_start, room_filter.time_end, room[1]))

        return free_rooms

    # [('Б-100', datetime.time(8, 30), datetime.time(10, 5), 'Корпус Б'),
    #  ('Б-100', datetime.time(16, 15), datetime.time(17, 50), 'Корпус Б'),
    #  ('Б-106А', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-106А', datetime.time(13, 35), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-108', datetime.time(12, 45), datetime.time(14, 20), 'Корпус Б'),
    #  ('Б-108', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-109', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-118', datetime.time(16, 15), datetime.time(17, 50), 'Корпус Б'),
    #  ('Б-118', datetime.time(17, 55), datetime.time(19, 30), 'Корпус Б'),
    #  ('Б-124/126', datetime.time(9, 20), datetime.time(10, 5), 'Корпус Б'),
    #  ('Б-124/126', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-124/126', datetime.time(12, 45), datetime.time(14, 20), 'Корпус Б'),
    #  ('Б-124/126', datetime.time(14, 30), datetime.time(15, 15), 'Корпус Б'),
    #  ('Б-124/126', datetime.time(15, 20), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-201', datetime.time(8, 30), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-201', datetime.time(12, 45), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-202', datetime.time(8, 30), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-202', datetime.time(12, 45), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-204', datetime.time(12, 45), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-205', datetime.time(8, 30), datetime.time(10, 5), 'Корпус Б'),
    #  ('Б-205', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-205', datetime.time(12, 45), datetime.time(14, 20), 'Корпус Б'),
    #  ('Б-205', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-205', datetime.time(16, 15), datetime.time(17, 50), 'Корпус Б'),
    #  ('Б-207', datetime.time(8, 30), datetime.time(10, 5), 'Корпус Б'),
    #  ('Б-207', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-207', datetime.time(12, 45), datetime.time(14, 20), 'Корпус Б'),
    #  ('Б-207', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-207', datetime.time(16, 15), datetime.time(17, 50), 'Корпус Б'),
    #  ('Б-208', datetime.time(8, 30), datetime.time(10, 5), 'Корпус Б'),
    #  ('Б-208', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-208', datetime.time(12, 45), datetime.time(14, 20), 'Корпус Б'),
    #  ('Б-208', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-208', datetime.time(16, 15), datetime.time(18, 40), 'Корпус Б'),
    #  ('Б-208', datetime.time(18, 45), datetime.time(20, 20), 'Корпус Б'),
    #  ('Б-210', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-210', datetime.time(11, 55), datetime.time(13, 30), 'Корпус Б'),
    #  ('Б-210', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-210', datetime.time(16, 15), datetime.time(17, 50), 'Корпус Б'),
    #  ('Б-210', datetime.time(20, 25), datetime.time(22, 0), 'Корпус Б'),
    #  ('Б-211', datetime.time(8, 30), datetime.time(13, 30), 'Корпус Б'),
    #  ('Б-211', datetime.time(13, 35), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-212', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-212', datetime.time(12, 45), datetime.time(14, 20), 'Корпус Б'),
    #  ('Б-212', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-212', datetime.time(16, 15), datetime.time(17, 50), 'Корпус Б'),
    #  ('Б-212ст', datetime.time(8, 30), datetime.time(10, 5), 'Корпус Б'),
    #  ('Б-212ст', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-212ст', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-212ст', datetime.time(16, 15), datetime.time(17, 50), 'Корпус Б'),
    #  ('Б-213', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-213', datetime.time(11, 55), datetime.time(13, 30), 'Корпус Б'),
    #  ('Б-213', datetime.time(13, 35), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-213', datetime.time(16, 15), datetime.time(17, 50), 'Корпус Б'),
    #  ('Б-213', datetime.time(18, 45), datetime.time(20, 20), 'Корпус Б'),
    #  ('Б-213', datetime.time(20, 25), datetime.time(22, 0), 'Корпус Б'),
    #  ('Б-214', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-214', datetime.time(12, 45), datetime.time(14, 20), 'Корпус Б'),
    #  ('Б-214', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-214', datetime.time(16, 15), datetime.time(17, 50), 'Корпус Б'),
    #  ('Б-214', datetime.time(19, 35), datetime.time(20, 20), 'Корпус Б'),
    #  ('Б-214', datetime.time(20, 25), datetime.time(22, 0), 'Корпус Б'),
    #  ('Б-215', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-215', datetime.time(11, 55), datetime.time(13, 30), 'Корпус Б'),
    #  ('Б-215', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-215', datetime.time(16, 15), datetime.time(18, 40), 'Корпус Б'),
    #  ('Б-215', datetime.time(20, 25), datetime.time(22, 0), 'Корпус Б'),
    #  ('Б-216', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-216', datetime.time(11, 55), datetime.time(13, 30), 'Корпус Б'),
    #  ('Б-216', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-216', datetime.time(16, 15), datetime.time(17, 50), 'Корпус Б'),
    #  ('Б-217', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-217', datetime.time(11, 55), datetime.time(13, 30), 'Корпус Б'),
    #  ('Б-217', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-217', datetime.time(20, 25), datetime.time(22, 0), 'Корпус Б'),
    #  ('Б-218', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-218', datetime.time(11, 55), datetime.time(13, 30), 'Корпус Б'),
    #  ('Б-218', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-218', datetime.time(17, 5), datetime.time(18, 40), 'Корпус Б'),
    #  ('Б-218', datetime.time(18, 45), datetime.time(20, 20), 'Корпус Б'),
    #  ('Б-218', datetime.time(20, 25), datetime.time(22, 0), 'Корпус Б'),
    #  ('Б-219', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-219', datetime.time(11, 55), datetime.time(13, 30), 'Корпус Б'),
    #  ('Б-219', datetime.time(16, 15), datetime.time(22, 0), 'Корпус Б'),
    #  ('Б-221', datetime.time(11, 5), datetime.time(12, 40), 'Корпус Б'),
    #  ('Б-221', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-221', datetime.time(16, 15), datetime.time(17, 50), 'Корпус Б'),
    #  ('Б-301', datetime.time(8, 30), datetime.time(10, 5), 'Корпус Б'),
    #  ('Б-301', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-301', datetime.time(11, 55), datetime.time(13, 30), 'Корпус Б'),
    #  ('Б-301', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-301', datetime.time(16, 15), datetime.time(17, 50), 'Корпус Б'),
    #  ('Б-303', datetime.time(8, 30), datetime.time(10, 5), 'Корпус Б'),
    #  ('Б-303', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-303', datetime.time(11, 55), datetime.time(13, 30), 'Корпус Б'),
    #  ('Б-303', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-303', datetime.time(16, 15), datetime.time(17, 50), 'Корпус Б'),
    #  ('Б-304', datetime.time(11, 55), datetime.time(13, 30), 'Корпус Б'),
    #  ('Б-304', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-308', datetime.time(12, 45), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-314а', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-314а', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-314б', datetime.time(12, 45), datetime.time(14, 20), 'Корпус Б'),
    #  ('Б-315', datetime.time(12, 45), datetime.time(14, 20), 'Корпус Б'),
    #  ('Б-315', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-316', datetime.time(11, 55), datetime.time(13, 30), 'Корпус Б'),
    #  ('Б-401', datetime.time(8, 30), datetime.time(10, 5), 'Корпус Б'),
    #  ('Б-401', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-401', datetime.time(11, 55), datetime.time(13, 30), 'Корпус Б'),
    #  ('Б-401', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-401', datetime.time(16, 15), datetime.time(17, 50), 'Корпус Б'),
    #  ('Б-403', datetime.time(8, 30), datetime.time(10, 5), 'Корпус Б'),
    #  ('Б-403', datetime.time(10, 15), datetime.time(11, 50), 'Корпус Б'),
    #  ('Б-403', datetime.time(11, 55), datetime.time(13, 30), 'Корпус Б'),
    #  ('Б-403', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('Б-403', datetime.time(16, 15), datetime.time(17, 50), 'Корпус Б'),
    #  ('каф.69', datetime.time(9, 20), datetime.time(11, 0), 'Корпус Б'),
    #  ('каф.69', datetime.time(11, 5), datetime.time(11, 50), 'Корпус Б'),
    #  ('каф.69', datetime.time(14, 30), datetime.time(16, 5), 'Корпус Б'),
    #  ('каф.69', datetime.time(16, 15), datetime.time(18, 40), 'Корпус Б')]

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
