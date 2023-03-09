# from timeit import timeit

from set_info import (
    parse_academic,
    parse_corps,
    parse_groups,
    parse_room,
    parse_schedule,
    parse_teachers,
    parse_teachers_fullname,
)


def main():
    print("--SET INFO--: Corps")
    parse_corps()
    print("Completed: Corps")
    print()

    print("--SET INFO--: Rooms")
    parse_room()
    print("Completed: Rooms")
    print()

    print("--SET INFO--: Academic")
    parse_academic()
    print("Completed: Academic")
    print()

    print("--SET INFO--: Groups")
    parse_groups()
    print("Completed: Groups")
    print()

    print("--PARSE INFO--: Teachers")
    parse_teachers()
    print("Completed: Teachers")
    print()

    print("--SET INFO--: Teachers fullname")
    parse_teachers_fullname()
    print("Completed: Teachers fullname")
    print()

    print("--SET INFO--: Schedule")
    parse_schedule()
    print("Completed: Schedule")
    print()

    # print("--SET INFO--: Translated schedule")
    # run("trans_to_db")
    # print("Completed: Translated schedule")
    # print()


if __name__ == '__main__':
    main()
