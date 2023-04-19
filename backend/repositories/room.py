import time
from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import and_, delete, exists, func, not_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import array_agg

from backend.database.models.association_tables import AT_lesson_room
from backend.database.models.corps import CorpsModel
from backend.database.models.lesson import LessonModel
from backend.database.models.room import RoomModel
from backend.filters.room import RoomFilter
from backend.schemas.room import RoomCreateSchema


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
    async def get_empty(db: AsyncSession, room_filter: RoomFilter) -> List[str]:
        _ = time.time()

        # busy_rooms_subq = (
        #     select(RoomModel.guid)
        #     .join(AT_lesson_room, AT_lesson_room.c.room_guid == RoomModel.guid)
        #     .join(LessonModel, LessonModel.guid == AT_lesson_room.c.lesson_guid)
        #     .join(CorpsModel, CorpsModel.guid == RoomModel.corps_guid)
        #     .where(
        #         and_(
        #             CorpsModel.name == room_filter.corps,
        #             room_filter.time_start >= LessonModel.time_start,
        #             room_filter.time_end <= LessonModel.time_end,
        #             or_(
        #                 LessonModel.date_start.is_(None),
        #                 exists().where(
        #                     and_(
        #                         room_filter.date_ >= LessonModel.date_start,
        #                         room_filter.date_ <= LessonModel.date_end
        #                     )
        #                 )
        #             )
        #         )
        #     )
        #     .distinct()
        # )
        #
        # empty_rooms = await db.execute(
        #     select(RoomModel.number)
        #     .join(CorpsModel, CorpsModel.guid == RoomModel.corps_guid)
        #     .where((RoomModel.guid.notin_(busy_rooms_subq)) & (CorpsModel.name == room_filter.corps))
        # )

        free_rooms_subq = (
            select(
                RoomModel.guid,  # add this column to the subquery
                RoomModel.number,
                array_agg(
                    func.concat(
                        LessonModel.date_start,
                        ' ',
                        LessonModel.time_start,
                        '-',
                        LessonModel.time_end
                    )
                ).label('free_times')
            )
            .select_from(RoomModel)
            .outerjoin(
                AT_lesson_room,
                AT_lesson_room.c.lesson_guid == LessonModel.guid,
            )
            .where(
                and_(
                    AT_lesson_room.c.room_guid == RoomModel.guid,  # use RoomModel.guid here
                    or_(
                        LessonModel.date_start.is_(None),
                        and_(
                            LessonModel.date_start <= room_filter.date_,
                            LessonModel.date_end >= room_filter.date_
                        )
                    ),
                    LessonModel.time_start <= room_filter.time_start,
                    LessonModel.time_end >= room_filter.time_end
                )
            )
            .join(CorpsModel, CorpsModel.guid == RoomModel.corps_guid)
            .where(CorpsModel.name == room_filter.corps)
            .group_by(RoomModel.number, RoomModel.guid)  # add RoomModel.guid to group_by
            .subquery()
        )

        empty_rooms = await db.execute(
            select(free_rooms_subq.c.number, free_rooms_subq.c.free_times)
            .select_from(free_rooms_subq)  # use the subquery instead of RoomModel
            .join(RoomModel, RoomModel.number == free_rooms_subq.c.number)  # add join condition
            .where(~exists().where(and_(
                AT_lesson_room.c.room_guid == free_rooms_subq.c.guid,  # use free_rooms_subq.c.guid here
                or_(
                    LessonModel.date_start.is_(None),
                    and_(
                        LessonModel.date_start <= room_filter.date_,
                        LessonModel.date_end >= room_filter.date_
                    )
                ),
                LessonModel.time_start <= room_filter.time_start,
                LessonModel.time_end >= room_filter.time_end,
            )))
        )

        res = empty_rooms.scalars().unique().all()
        print(res)

        print(f'Time: {time.time() - _}')
        return []

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
