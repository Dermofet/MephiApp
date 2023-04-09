import asyncio
import sys
import time

sys.path.append("/api")

from backend.database.connection import get_session_return
from parsing.parsers.room_parser import RoomParser
from parsing.parsers.schedule_parser import ScheduleParser
from parsing.parsers.teachers_fullname_parser import TeachersFullnameParser


async def set_schedule():
    db = await get_session_return()
    schedule_parser = ScheduleParser()
    await schedule_parser.parse_schedule()
    await db.close()


async def set_rooms():
    db = await get_session_return()
    room_parser = RoomParser()
    await room_parser.parse_room()
    await db.close()


async def set_teachers():
    db = await get_session_return()
    teacher_parser = TeachersFullnameParser()
    await teacher_parser.parse_teachers_fullname()
    await db.close()


def parse_all():
    _ = time.time()

    loop = asyncio.get_event_loop()

    try:
        print("\n---> Parsing schedule")
        loop.run_until_complete(set_schedule())
        print()
        print("\n---> Parsing schedule completed")
        print()

        print("\n---> Parsing rooms")
        loop.run_until_complete(set_rooms())
        print("\n---> Parsing rooms completed")
        print()

        print("\n---> Parsing teachers")
        loop.run_until_complete(set_teachers())
        print("\n---> Parsing teachers completed")
        print()
    except Exception as err:
        print(f"Error: {err}")
        loop.stop()
    finally:
        loop.close()

    print(f'Time: {time.time() - _}')


if __name__ == '__main__':
    parse_all()
