import asyncio
import time
import traceback

from app.backend.config import config
from app.backend.database.connection import get_session
from bulk_insert import *
from parsers.room_parser import RoomParser
from parsers.schedule_parser import ScheduleParser
from parsers.teachers_fullname_parser import TeachersFullnameParser
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://postgres:postgres@db/schedule",
    echo=config.DEBUG,
    pool_size=20,
    max_overflow=30,
    pool_timeout=60
)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def set_corps():
    db = await get_session()
    await bulk_insert_corps(db)


async def set_rooms():
    db = await get_session()
    await bulk_insert_room(db)


async def set_academic():
    db = await get_session()
    await bulk_insert_academic(db)


async def set_groups():
    db = await get_session()
    await bulk_insert_groups(db)


async def set_teachers():
    db = await get_session()
    await bulk_insert_teachers_fullname(db)


async def set_schedule():
    db = await get_session()
    await bulk_insert_schedule(db)


if __name__ == '__main__':
    _ = time.time()

    loop = asyncio.get_event_loop()

    try:
        print("--SET INFO--: Corps")
        loop.run_until_complete(set_corps())
        print("Completed: Corps")
        print()

        print("--SET INFO--: Rooms")
        loop.run_until_complete(set_rooms())
        print("Completed: Rooms")
        print()

        print("--SET INFO--: Academic")
        loop.run_until_complete(set_academic())
        print("Completed: Academic")
        print()

        print("--SET INFO--: Groups")
        loop.run_until_complete(set_groups())
        print("Completed: Groups")
        print()

        print("--PARSE INFO--: Teachers")
        loop.run_until_complete(set_teachers())
        print("Completed: Teachers")
        print()

        print("--SET INFO--: Schedule")
        loop.run_until_complete(set_schedule())
        print("Completed: Schedule")
        print()

        # print("--SET INFO--: Translated schedule")
        # run("trans_to_db")
        # print("Completed: Translated schedule")
        # print()
    except Exception as err:
        print(f"Error: {err}")
        loop.stop()
    finally:
        loop.close()

    print(f'Time: {time.time() - _}')
