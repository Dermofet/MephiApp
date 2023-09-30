import datetime
from typing import Dict, List, Tuple

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import and_, delete, not_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.database.dao.corps import CorpsDAO
from backend.api.database.dao.start_semester import StartSemesterDAO
from backend.api.database.models.association_tables import AT_lesson_room
from backend.api.database.models.corps import CorpsModel
from backend.api.database.models.lesson import LessonModel
from backend.api.database.models.room import RoomModel
from backend.api.filters.room import RoomFilter
from backend.api.schemas.room import RoomCreateSchema


class RoomDAO:
    """
    DAO для работы с комнатами
    """

    _session: AsyncSession

    weekdays = {
    0: "Понедельник",
    1: "Вторник",
    2: "Среда",
    3: "Четверг",
    4: "Пятница",
    5: "Суббота",
    6: "Воскресенье"
}

    def __init__(self, session: AsyncSession):
        self._session = session

    """
    Создание комнаты
    """
    async def create(self, data: RoomCreateSchema, corps_guid) -> RoomModel:
        room = RoomModel(number=data.number, corps_guid=corps_guid)

        self._session.add(room)
        await self._session.flush()
        await self._session.refresh(room)

        return room

    """
    Обновление комнаты
    """
    async def bulk_insert(self, data: List[RoomCreateSchema]) -> None:
        db_rooms = []
        corps_dao = CorpsDAO(self._session)

        for room in data:
            corps = await corps_dao.get_by_name(room.corps)
            db_rooms.append(RoomModel(number=room.number, corps_guid=corps.guid if corps else None))

        self._session.add_all(db_rooms)
        await self._session.flush()

    """
    Получение комнаты по id
    """
    async def get_by_id(self, guid: UUID4) -> RoomModel:
        room = await self._session.execute(select(RoomModel).where(RoomModel.guid == guid).limit(1))
        return room.scalar()

    """
    Получение всех комнат
    """
    async def get_all(self) -> List[RoomModel]:
        rooms = await self._session.execute(select(RoomModel))
        return rooms.scalars().unique().all()

    """
    Получение комнаты по номеру
    """
    async def get_by_number(self, number: str) -> RoomModel:
        room = await self._session.execute(select(RoomModel).where(RoomModel.number == number).limit(1))
        return room.scalar()

    """
    Получение комнаты пустой
    """
    async def get_empty(self, room_filter: RoomFilter, corps: List[str]) -> List[Tuple[str, datetime.time, datetime.time, str]]:
        start_semester_dao = StartSemesterDAO(self._session)

        date = await start_semester_dao.get()

        if date is None:
            raise HTTPException(409, "Даты начала семестра нет")

        week = [1, 2] if (((room_filter.date_ - date.date).days + 1) // 7 + 1) % 2 == 1 else [0, 2]

        weekdays = {
            0: "Понедельник",
            1: "Вторник",
            2: "Среда",
            3: "Четверг",
            4: "Пятница",
            5: "Суббота",
            6: "Воскресенье"
        }

        occupied_rooms = await self._get_occupied_rooms(room_filter, corps, week, weekdays)
        full_time_free_rooms = await self._get_full_time_free_rooms(corps, occupied_rooms)
        return self._get_free_rooms(room_filter, occupied_rooms, full_time_free_rooms)

    async def _get_occupied_rooms(self, room_filter: RoomFilter, corps: List[str], week: List[int], weekdays: Dict[int, str]) -> \
        List[Tuple[str, datetime.time, datetime.time, str]]:
        occupied_rooms = await self._session.execute(
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

        return occupied_rooms.all()

    async def _get_full_time_free_rooms(self, corps: List[str], occupied_rooms: List[Tuple[str, datetime.time, datetime.time, str]]) -> \
        List[Tuple[str, str]]:
        occupied_rooms_numbers = (room[0] for room in occupied_rooms)
        full_time_free_rooms = await self._session.execute(
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

        return full_time_free_rooms.all()

    def _get_free_rooms(
        self, 
        room_filter: RoomFilter, 
        occupied_rooms: List[Tuple[str, datetime.time, datetime.time, str]], 
        full_time_free_rooms: List[Tuple[str, str]]
    ) -> List[Tuple[str, datetime.time, datetime.time, str]]:
        last_room = None
        free_rooms = []
        deltatime = datetime.timedelta(minutes=10)
        for room in occupied_rooms:
            if last_room is None:
                if room[1] > room_filter.time_start and \
                            self._sub_time(room[1], room_filter.time_start) > deltatime:
                    free_rooms.append((room[0], room_filter.time_start, room[1], room[3]))
                last_room = room
                continue

            if last_room[0] == room[0]:
                if self._sub_time(last_room[2], room[1]) > deltatime:
                    free_rooms.append((last_room[0], last_room[2], room[1], last_room[3]))
                last_room = room
                continue

            if last_room[2] < room_filter.time_end and \
                        self._sub_time(last_room[2], room_filter.time_end) > deltatime:
                free_rooms.append((last_room[0], last_room[2], room_filter.time_end, last_room[3]))

            if room[1] > room_filter.time_start and \
                        self._sub_time(room[1], room_filter.time_start) > deltatime:
                free_rooms.append((room[0], room_filter.time_start, room[1], room[3]))
            last_room = room

        free_rooms.extend(
            (room[0], room_filter.time_start, room_filter.time_end, room[1])
            for room in full_time_free_rooms
        )
        return free_rooms

    """
    Получение даты начала семестра
    """
    @staticmethod
    def _sub_time(time1: datetime.time, time2: datetime.time) -> datetime.timedelta:
        datetime1 = datetime.datetime.combine(datetime.date.today(), time1)
        datetime2 = datetime.datetime.combine(datetime.date.today(), time2)
        return datetime2 - datetime1

    async def get_corps(self, room: RoomModel) -> CorpsModel:
        corps = await self._session.execute(select(CorpsModel).where(CorpsModel.guid == room.corps_guid).limit(1))
        return corps.scalar()

    """
    Получение даты начала семестра
    """
    async def update(self, guid: UUID4, data: RoomCreateSchema) -> RoomModel:
        room = await self.get_by_id(guid)

        if room is None:
            HTTPException(status_code=404, detail="Кабинет не найден")

        room = await self._session.execute(update(RoomModel).where(RoomModel.guid == guid).values(**data.model_dump()))
        await self._session.flush()
        await self._session.refresh(room)
        return room

    """
    Удаление комнаты
    """
    async def delete(self, guid: UUID4) -> None:
        await self._session.execute(delete(RoomModel).where(RoomModel.guid == guid))
        await self._session.flush()