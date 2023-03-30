import sys

sys.path.append("/app")

from parsers.room_parser import RoomParser
from parsers.schedule_parser import ScheduleParser
from parsers.teachers_fullname_parser import TeachersFullnameParser


def parse_all():
    print("\n---> Parsing schedule")
    schedule_parser = ScheduleParser()
    schedule_parser.parse_schedule()
    print()
    print("\n---> Parsing schedule completed")
    print()

    print("\n---> Parsing rooms")
    room_parser = RoomParser()
    room_parser.parse_room()
    print("\n---> Parsing rooms")
    print()

    print("\n---> Parsing teachers")
    teacher_parser = TeachersFullnameParser()
    teacher_parser.parse_teachers_fullname()
    print("\n---> Parsing teachers")
    print()


if __name__ == '__main__':
    parse_all()
