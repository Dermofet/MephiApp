import asyncio
import sys
import time

sys.path.append("/api")

from bulk_insert_schedule import *

from backend.database.connection import get_session_return, get_session_yield
from parsing import config
from parsing.parsers.room_parser import RoomParser
from parsing.parsers.schedule_parser import ScheduleParser
from parsing.parsers.teachers_fullname_parser import TeachersFullnameParser


async def set_corps():
    db = await get_session_return()
    await bulk_insert_corps(db)
    await db.close()


async def set_rooms():
    db = await get_session_return()
    await bulk_insert_room(db)
    await db.close()


async def set_academic():
    db = await get_session_return()
    await bulk_insert_academic(db)
    await db.close()


async def set_groups():
    db = await get_session_return()
    await bulk_insert_groups(db)
    await db.close()


async def set_teachers():
    db = await get_session_return()
    await bulk_insert_teachers(db)
    await db.close()


async def set_translated_teachers(langs: list[str]):
    db = await get_session_return()
    await bulk_translated_teachers(db, langs)
    await db.close()


async def set_schedule():
    db = await get_session_return()
    await bulk_insert_schedule(db)
    await db.close()


async def set_translated_schedule(langs: list[str]):
    db = await get_session_return()
    await bulk_translated_schedule(db, langs)
    await db.close()


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

        print("--SET INFO--: Translated teachers")
        loop.run_until_complete(set_translated_teachers(["en"]))
        print("Completed: Translated teachers")
        print()

        print("--SET INFO--: Schedule")
        loop.run_until_complete(set_schedule())
        print("Completed: Schedule")
        print()

        print("--SET INFO--: Translated schedule")
        loop.run_until_complete(set_translated_schedule(config.FOREIGN_LANGS))
        print("Completed: Translated schedule")
        print()
    # except Exception as err:
    #     print(f"Error: {err}")
    #     loop.stop()
    finally:
        loop.close()

    print(f'Time: {time.time() - _}')
