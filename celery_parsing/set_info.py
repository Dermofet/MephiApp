import json
from os import getcwd
from typing import Optional

from worker import Worker

from backend.schemas.academic import AcademicCreateSchema
from backend.schemas.corps import CorpsCreateSchema
from backend.schemas.group import GroupCreateSchema
from backend.schemas.lesson import LessonCreateSchema
from backend.schemas.room import RoomCreateSchema
from backend.schemas.teacher import TeacherCreateSchema
from celery_parsing.connection import celery
from parsing.parsers.schedule_parser import ScheduleParser


def parse_academic() -> None:
    parser = ScheduleParser()
    res = []
    for academic in parser.getAcademicTypes():
        _academic_ = {
            "name": academic[0],
        }
        res.append(json.dumps(_academic_, ensure_ascii=False))
    celery.send_task("academic_create", res)


def parse_groups() -> None:
    parser = ScheduleParser()
    res = []
    for academic in parser.getAcademicTypes():
        try:
            with open(f'..\\parsing\\schedule\\{academic[0]}.json', 'r', encoding='utf-8') as fp:
                print(f'Filename: {academic[0]}.json')
                dict_json = json.loads(fp.read().replace("'", '\''))
                for course in dict_json['courses']:
                    for group in course['groups']:
                        _group_ = {
                            "name": group['name'],
                            "course": course['name'],
                            "academic": dict_json['name'],
                        }
                        res.append(json.dumps(_group_, ensure_ascii=False))
        except FileNotFoundError:
            print(f'File {academic[0]}.json was not found.')
    celery.send_task("group_create", res)


def parse_schedule() -> None:
    parser = ScheduleParser()
    res = []
    for academic in parser.getAcademicTypes():
        try:
            with open(f'..\\parsing\\schedule\\{academic[0]}.json', 'r', encoding='utf-8') as fp:
                print(f'Filename: {academic[0]}.json')
                dict_json = json.loads(fp.read().replace("'", '\''))
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
                                            res.append(json.dumps(_lesson_, ensure_ascii=False))
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
                                        res.append(json.dumps(_lesson_, ensure_ascii=False))
        except FileNotFoundError:
            print(f'File {academic[0]}.json was not found.')
    celery.send_task("lesson_create", res)


def parse_teachers() -> None:
    parser = ScheduleParser()
    res = []
    for academic in parser.getAcademicTypes():
        try:
            with open(f'..\\parsing\\schedule\\{academic[0]}.json', 'r', encoding='utf-8') as fp:
                print(f'Filename: {academic[0]}.json')
                dict_json = json.loads(fp.read().replace("'", '\''))
                teachers = set()
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
                                                res.append(json.dumps(_teacher_, ensure_ascii=False))
                                                teachers.add(teacher)
        except FileNotFoundError:
            print(f'File {academic[0]}.json was not found.')
    celery.send_task("teacher_create", res)


def parse_room() -> None:
    try:
        with open(f'..\\parsing\\rooms\\rooms.json', 'r', encoding='utf-8') as fp:
            print(f'Filename: rooms.json')
            dict_json = json.loads(fp.read().replace("'", '\''))
            res = []
            for room in dict_json['rooms']:
                res.append(json.dumps(room, ensure_ascii=False))
            celery.send_task("room_create", res)
    except FileNotFoundError:
        print(f'File rooms.json was not found.')


def parse_corps() -> None:
    try:
        with open(f'..\\parsing\\rooms\\rooms.json', 'r', encoding='utf-8') as fp:
            print(f'Filename: rooms.json')
            dict_json = json.loads(fp.read().replace("'", '\''))
            res = []
            for corps in dict_json['corps']:
                res.append(json.dumps(corps, ensure_ascii=False))
            celery.send_task("corps_create", res)
    except FileNotFoundError:
        print(f'File rooms.json was not found.')


def parse_teachers_fullname() -> None:
    try:
        with open(f'..\\parsing\\teachers\\TeachersFullname.json', 'r', encoding='utf-8') as fp:
            print(f'Filename: TeachersFullname.json')
            dict_json = json.loads(fp.read().replace("'", '\''))
            res = []
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
                res.append(json.dumps(_teacher_, ensure_ascii=False))
            celery.send_task("teacher_update", res)
    except FileNotFoundError:
        print(f'File TeachersFullname.json was not found. {getcwd()}')
