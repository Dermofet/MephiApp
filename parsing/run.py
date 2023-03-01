import asyncio
import time

from set_info import (
    start_parse_academic,
    start_parse_corps,
    start_parse_fullname,
    start_parse_groups,
    start_parse_room,
    start_parse_schedule,
    start_parse_teachers,
)

from parsing.parsers.room_parser import RoomParser
from parsing.parsers.schedule_parser import ScheduleParser
from parsing.parsers.teachers_fullname_parser import TeachersFullnameParser
from parsing.pool import Pool


def run(mode: str):
    if mode == "parse_schedule":
        parser = ScheduleParser()
        parser.parse_schedule()
    elif mode == "parse_rooms":
        parser = RoomParser()
        parser.parse_room()
    elif mode == "parse_fullname":
        parser = TeachersFullnameParser()
        parser.parse_teachers_fullname()
    elif mode == "schedule_to_db":
        loop = asyncio.get_event_loop()
        pool = Pool(30)
        try:
            loop.run_until_complete(start_parse_schedule(pool))
        except KeyboardInterrupt:
            loop.run_until_complete(pool.stop())
            loop.close()
    elif mode == "rooms_to_db":
        loop = asyncio.get_event_loop()
        pool = Pool(30)
        try:
            loop.run_until_complete(start_parse_room(pool))
        except KeyboardInterrupt:
            loop.run_until_complete(pool.stop())
            loop.close()
    elif mode == "corps_to_db":
        loop = asyncio.get_event_loop()
        pool = Pool(30)
        try:
            loop.run_until_complete(start_parse_corps(pool))
        except KeyboardInterrupt:
            loop.run_until_complete(pool.stop())
            loop.close()
    elif mode == "academics_to_db":
        loop = asyncio.get_event_loop()
        pool = Pool(30)
        try:
            loop.run_until_complete(start_parse_academic(pool))
        except KeyboardInterrupt:
            loop.run_until_complete(pool.stop())
            loop.close()
    elif mode == "groups_to_db":
        loop = asyncio.get_event_loop()
        pool = Pool(30)
        try:
            loop.run_until_complete(start_parse_groups(pool))
        except KeyboardInterrupt:
            loop.run_until_complete(pool.stop())
            loop.close()
    elif mode == "teachers_to_db":
        loop = asyncio.get_event_loop()
        pool = Pool(30)
        try:
            loop.run_until_complete(start_parse_teachers(pool))
        except KeyboardInterrupt:
            loop.run_until_complete(pool.stop())
            loop.close()
    elif mode == "fullname_to_db":
        loop = asyncio.get_event_loop()
        pool = Pool(30)
        try:
            loop.run_until_complete(start_parse_fullname(pool))
        except KeyboardInterrupt:
            loop.run_until_complete(pool.stop())
            loop.close()


if __name__ == '__main__':
    print("--PARSE INFO--: Schedule")
    run("parse_schedule")
    print("Completed: Schedule")
    print()

    print("--PARSE INFO--: Rooms")
    run("parse_rooms")
    print("Completed: Rooms")
    print()

    _ = time.time()

    print("--SET INFO--: Corps")
    run("corps_to_db")
    print("Completed: Corps")
    print()

    print("--SET INFO--: Rooms")
    run("rooms_to_db")
    print("Completed: Rooms")
    print()

    print("--SET INFO--: Academic")
    run("academics_to_db")
    print("Completed: Academic")
    print()

    print("--SET INFO--: Groups")
    run("groups_to_db")
    print("Completed: Groups")
    print()

    print("--PARSE INFO--: Teachers")
    run("teachers_to_db")
    print("Completed: Teachers")
    print()

    print("--SET INFO--: Teachers fullname")
    run("fullname_to_db")
    print("Completed: Teachers fullname")
    print()

    print("--SET INFO--: Schedule")
    run("schedule_to_db")
    print("Completed: Schedule")
    print()

    print(f'Time: {time.time() - _}')
