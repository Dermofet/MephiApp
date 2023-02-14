import json
from os import getcwd
from typing import Optional

from parsing.parsers.schedule_parser import ScheduleParser
from parsing.pool import Pool
from parsing.task import PostTask, PutTask


def parse_academic() -> list[PostTask]:
    res = []
    parser = ScheduleParser()
    i = 1
    for academic in parser.getAcademicTypes():
        _academic_ = {
            "name": academic[0],
        }
        json_academic = json.dumps(_academic_, ensure_ascii=False)
        res.append(PostTask(tid=i,
                            str_json=json_academic,
                            url='http://127.0.0.1:8000/api/academic',
                            description='Academic POST'))
        i += 1
    return res


def parse_groups() -> list[PostTask]:
    res = []
    parser = ScheduleParser()
    i = 1
    for academic in parser.getAcademicTypes():
        try:
            with open(f'{getcwd()}\\schedule\\{academic[0]}.json', 'r', encoding='utf-8') as fp:
                print(f'Filename: {academic[0]}.json')
                dict_json = json.loads(fp.read().replace("'", '\''))
                for course in dict_json['courses']:
                    for group in course['groups']:
                        _group_ = {
                            "name": group['name'],
                            "course": course['name'],
                            "academic": dict_json['name'],
                        }
                        json_group = json.dumps(_group_, ensure_ascii=False)
                        res.append(PostTask(tid=i,
                                            str_json=json_group,
                                            url='http://127.0.0.1:8000/api/group',
                                            description='Group POST'))
                        i += 1
        except FileNotFoundError as err:
            print(f'File {academic[0]}.json was not found.')
    return res


def parse_schedule() -> list[PostTask]:
    res = []
    parser = ScheduleParser()
    i = 1
    for academic in parser.getAcademicTypes():
        try:
            with open(f'{getcwd()}\\schedule\\{academic[0]}.json', 'r', encoding='utf-8') as fp:
                print(f'Filename: {academic[0]}.json')
                dict_json = json.loads(fp.read().replace("'", '\''))
                teachers = []
                for course in dict_json['courses']:
                    for group in course['groups']:
                        for day in group['schedule']:
                            for lesson in day['lessons']:
                                for lesson_var in lesson['lesson']:
                                    if len(lesson_var['teacher_name']) > 0:
                                        for teacher in lesson_var['teacher_name']:
                                            _lesson_ = {
                                                "time_start": lesson['time_start'],
                                                "time_end": lesson['time_end'],
                                                "dot": lesson_var['dot'],
                                                "weeks": lesson_var['weeks'],
                                                "day": day['day'],
                                                "date_start": lesson_var['date_start'],
                                                "date_end": lesson_var['date_end'],
                                                "type": lesson_var['lesson_type'],
                                                "name": lesson_var['lesson_name'],
                                                "subgroup": lesson_var['subgroup'],
                                                "group": group['name'],
                                                "course": course['name'],
                                                "room": lesson_var['room'],
                                                "academic": dict_json['name'],
                                                "teacher_name": teacher,
                                                "lang": "ru",
                                            }

                                            json_lesson = json.dumps(_lesson_, ensure_ascii=False)

                                            res.append(PostTask(tid=i,
                                                                str_json=json_lesson,
                                                                url='http://127.0.0.1:8000/api/lesson',
                                                                description='Lesson POST'))
                                            i += 1
                                    else:
                                        _lesson_ = {
                                            "time_start": lesson['time_start'],
                                            "time_end": lesson['time_end'],
                                            "dot": lesson_var['dot'],
                                            "weeks": lesson_var['weeks'],
                                            "day": day['day'],
                                            "date_start": lesson_var['date_start'],
                                            "date_end": lesson_var['date_end'],
                                            "type": lesson_var['lesson_type'],
                                            "name": lesson_var['lesson_name'],
                                            "subgroup": lesson_var['subgroup'],
                                            "group": group['name'],
                                            "course": course['name'],
                                            "room": lesson_var['room'],
                                            "academic": dict_json['name'],
                                            "teacher_name": None,
                                            "lang": "ru",
                                        }

                                        json_lesson = json.dumps(_lesson_, ensure_ascii=False)

                                        res.append(PostTask(tid=i,
                                                            str_json=json_lesson,
                                                            url='http://127.0.0.1:8000/api/lesson',
                                                            description='Lesson POST'))
                                        i += 1
        except FileNotFoundError as err:
            print(f'File {academic[0]}.json was not found.')
    return res


def parse_teachers() -> list[PostTask]:
    res = []
    parser = ScheduleParser()
    i = 1
    for academic in parser.getAcademicTypes():
        try:
            with open(f'{getcwd()}\\schedule\\{academic[0]}.json', 'r', encoding='utf-8') as fp:
                print(f'Filename: {academic[0]}.json')
                dict_json = json.loads(fp.read().replace("'", '\''))
                teachers = []
                for course in dict_json['courses']:
                    for group in course['groups']:
                        for day in group['schedule']:
                            for lesson in day['lessons']:
                                for lesson_var in lesson['lesson']:
                                    if len(lesson_var['teacher_name']) > 0:
                                        for teacher in lesson_var['teacher_name']:
                                            if teacher not in teachers:
                                                _teacher_ = {
                                                    "online_url": None,
                                                    "alt_online_url": None,
                                                    "lang": "ru",
                                                    "name": teacher,
                                                    "fullname": None,
                                                }
                                                json_teacher = json.dumps(_teacher_, ensure_ascii=False)
                                                res.append(PostTask(tid=i,
                                                                    str_json=json_teacher,
                                                                    url='http://127.0.0.1:8000/api/teacher',
                                                                    description='Teacher POST'))
                                                i += 1
                                                teachers.append(teacher)
        except FileNotFoundError as err:
            print(f'File {academic[0]}.json was not found.')
    return res


def parse_room() -> list[PostTask]:
    res = []
    i = 1
    try:
        with open(f'{getcwd()}\\rooms\\rooms.json', 'r', encoding='utf-8') as fp:
            print(f'Filename: rooms.json')
            dict_json = json.loads(fp.read().replace("'", '\''))
            for room in dict_json['rooms']:
                json_room = json.dumps(room, ensure_ascii=False)
                res.append(PostTask(tid=i,
                                    str_json=json_room,
                                    url='http://127.0.0.1:8000/api/room',
                                    description='Room POST'))
                i += 1
    except FileNotFoundError as err:
        print(f'File {academic[0]}.json was not found.')
    return res


def parse_corps() -> list[PostTask]:
    res = []
    i = 1
    try:
        with open(f'{getcwd()}\\rooms\\rooms.json', 'r', encoding='utf-8') as fp:
            print(f'Filename: rooms.json')
            dict_json = json.loads(fp.read().replace("'", '\''))
            for corps in dict_json['corps']:
                json_corps = json.dumps(corps, ensure_ascii=False)
                res.append(PostTask(tid=i,
                                    str_json=json_corps,
                                    url='http://127.0.0.1:8000/api/corps',
                                    description='Corps POST'))
                i += 1
    except FileNotFoundError as err:
        print(f'File rooms.json was not found.')
    return res


def parse_teachers_fullname() -> list[PostTask]:
    res = []
    i = 1
    try:
        with open(f'{getcwd()}\\teachers\\TeachersFullname.json', 'r', encoding='utf-8') as fp:
            print(f'Filename: TeachersFullname.json')
            dict_json = json.loads(fp.read().replace("'", '\''))
            for fullname in dict_json['teachers_fullname']:
                buffer = fullname.split()
                if len(buffer) == 2:
                    shortname = buffer[0] + " " + buffer[1][0] + "."
                else:
                    shortname = buffer[0] + " " + buffer[1][0] + "." + buffer[2][0] + "."
                _teacher_ = {
                    "online_url": None,
                    "alt_online_url": None,
                    "lang": "ru",
                    "name": shortname,
                    "fullname": fullname
                }
                json_fullname = json.dumps(_teacher_, ensure_ascii=False)
                res.append(PutTask(tid=i,
                                   str_json=json_fullname,
                                   url='http://127.0.0.1:8000/api/teacher',
                                   description='Teacher PUT'))
                i += 1
    except FileNotFoundError as err:
        print(f'File rooms.json was not found.')
    return res


async def start_parse_schedule(pool: Pool):
    tasks = parse_schedule()
    for task in tasks:
        await pool.put(task)
    pool.start()
    await pool.join()
    await pool.stop()


async def start_parse_room(pool: Pool):
    tasks = parse_room()
    for task in tasks:
        await pool.put(task)
    pool.start()
    await pool.join()
    await pool.stop()


async def start_parse_corps(pool: Pool):
    tasks = parse_corps()
    for task in tasks:
        await pool.put(task)
    pool.start()
    await pool.join()
    await pool.stop()


async def start_parse_academic(pool: Pool):
    tasks = parse_academic()
    for task in tasks:
        await pool.put(task)
    pool.start()
    await pool.join()
    await pool.stop()


async def start_parse_groups(pool: Pool):
    tasks = parse_groups()
    for task in tasks:
        await pool.put(task)
    pool.start()
    await pool.join()
    await pool.stop()


async def start_parse_teachers(pool: Pool):
    tasks = parse_teachers()
    for task in tasks:
        await pool.put(task)
    pool.start()
    await pool.join()
    await pool.stop()


async def start_parse_fullname(pool: Pool):
    tasks = parse_teachers_fullname()
    for task in tasks:
        await pool.put(task)
    pool.start()
    await pool.join()
    await pool.stop()
