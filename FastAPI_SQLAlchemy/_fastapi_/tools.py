from .db import schemas
import FastAPI_SQLAlchemy.translator.translator as tr

from sqlalchemy.orm import Session

import datetime
from typing import Union
import collections
import time

DayChanger = {
    "monday": "1",
    "tuesday": "2",
    "wednesday": "3",
    "thursday": "4",
    "friday": "5",
    "saturday": "6"
}
TimeTemplate = [
    {"lesson": 0, "min": "08:30", "max": "10:05"},
    {"lesson": 1, "min": "10:15", "max": "11:45"},
    {"lesson": 2, "min": "11:55", "max": "14:20"},
    {"lesson": 3, "min": "14:30", "max": "16:05"},
    {"lesson": 4, "min": "16:15", "max": "17:45"},
    {"lesson": 5, "min": "17:55", "max": "20:20"},
    {"lesson": 6, "min": "20:25", "max": "21:10"},
    {"lesson": 7, "min": "21:20", "max": "22:50"}]


def output_From_DBLesson(db_lessons: list, db: Session, dest='en'):
    lessons = {"schedule":
        {
            "1": {
                "lessons": [[], [], [], [], [], [], [], []]
            },
            "2": {
                "lessons": [[], [], [], [], [], [], [], []]
            },
            "3": {
                "lessons": [[], [], [], [], [], [], [], []]
            },
            "4": {
                "lessons": [[], [], [], [], [], [], [], []]
            },
            "5": {
                "lessons": [[], [], [], [], [], [], [], []]
            },
            "6": {
                "lessons": [[], [], [], [], [], [], [], []]
            },
        }
    }

    db_lessons = set(db_lessons)

    if dest == 'ru':
        for db_lesson in db_lessons:
            if check_date(db_lesson.date_start, db_lesson.date_end):
                schemas_lesson = schemas.LessonOutput(item=db_lesson, db=db)

                if schemas_lesson.type == 'Лек':
                    schemas_lesson.type = "Лекция"
                elif schemas_lesson.type == 'Пр':
                    schemas_lesson.type = "Практика"
                elif schemas_lesson.type == 'Лаб':
                    schemas_lesson.type = "Лабораторная работа"

                for time_ in TimeTemplate:
                    if time_["min"] <= schemas_lesson.time_start <= time_["max"]:
                        lessons["schedule"][DayChanger[db_lesson.day]]["lessons"][time_["lesson"]].append(schemas_lesson)
                        break
    else:
        trans = ""
        schemas_lessons = []
        schemas_lesson_day = []
        for db_lesson in db_lessons:
            if check_date(db_lesson.date_start, db_lesson.date_end):
                schemas_lesson = schemas.LessonOutput(item=db_lesson, db=db)
                schemas_lessons.append(schemas_lesson)
                schemas_lesson_day.append(db_lesson.day)
                trans += schemas_lesson.translate_str()
        _ = time.time()
        trans = tr.translate(trans, dest=dest)
        print(time.time() - _)
        for i, field in enumerate(trans.split("|")[:-1], start=1):
            items = field.split(" + ")

            # name
            schemas_lessons[i - 1].name = delete_spaces(items[0])

            # teacher_name
            schemas_lessons[i - 1].tr_teacher_name = []
            if items[1].find("#") == -1:
                schemas_lessons[i - 1].tr_teacher_name.extend(
                    delete_spaces(item) for item in items[1].split(" _ ")
                )
            # teacher_fullname
            schemas_lessons[i - 1].tr_teacher_fullname = []
            if items[2].find("#") == -1:
                schemas_lessons[i - 1].tr_teacher_fullname.extend(
                    delete_spaces(item) for item in items[2].split(" _ ")
                )
            # subgroup
            schemas_lessons[i - 1].subgroup = (
                delete_spaces(items[3]) if items[3].find("#") == -1 else None
            )
            # type
            if items[4].find("#") == -1:
                schemas_lessons[i - 1].type = delete_spaces(items[4])
            else:
                schemas_lessons[i - 1].type = None

            for time_ in TimeTemplate:
                if time_["min"] <= schemas_lessons[i - 1].time_start <= time_["max"]:
                    lessons["schedule"][DayChanger[schemas_lesson_day[i - 1]]]["lessons"][time_["lesson"]].append(
                        schemas_lessons[i - 1])
                    break
    return lessons


def output_From_DBLessonT(db_lessons: list, db: Session, dest='en'):
    lessons = {"schedulet":
        {
            "1": {
                "lessons": [[], [], [], [], [], [], [], []]
            },
            "2": {
                "lessons": [[], [], [], [], [], [], [], []]
            },
            "3": {
                "lessons": [[], [], [], [], [], [], [], []]
            },
            "4": {
                "lessons": [[], [], [], [], [], [], [], []]
            },
            "5": {
                "lessons": [[], [], [], [], [], [], [], []]
            },
            "6": {
                "lessons": [[], [], [], [], [], [], [], []]
            },
        }
    }

    buffer_lessons = []
    if dest == 'ru':
        for db_lesson in db_lessons:
            if db_lesson in buffer_lessons:
                continue
            buffer_lessons.append(db_lesson)
            if check_date(db_lesson.date_start, db_lesson.date_end):
                schemas_lesson = schemas.LessonOutputT(item=db_lesson, db=db)

                if schemas_lesson.type == 'Лек':
                    schemas_lesson.type = "Лекция"
                elif schemas_lesson.type == 'Пр':
                    schemas_lesson.type = "Практика"
                elif schemas_lesson.type == 'Лаб':
                    schemas_lesson.type = "Лабораторная работа"

                for time in TimeTemplate:
                    if time["min"] <= schemas_lesson.time_start <= time["max"]:
                        lessons["schedulet"][DayChanger[db_lesson.day]]["lessons"][time["lesson"]].append(
                            schemas_lesson)
                        break
    else:
        trans = ""
        schemas_lessons = []
        schemas_lesson_day = []
        for db_lesson in db_lessons:
            if db_lesson in buffer_lessons:
                continue
            buffer_lessons.append(db_lesson)
            if check_date(db_lesson.date_start, db_lesson.date_end):
                schemas_lesson = schemas.LessonOutputT(item=db_lesson, db=db)
                schemas_lessons.append(schemas_lesson)
                schemas_lesson_day.append(db_lesson.day)
                trans += schemas_lesson.translate_str()

        trans = tr.translate(trans, dest=dest)

        for i, field in enumerate(trans.split("|")[:-1], start=1):
            items = field.split(" + ")
            # name
            schemas_lessons[i - 1].name = delete_spaces(items[0])

            # subgroup
            schemas_lessons[i - 1].subgroup = (
                delete_spaces(items[1]) if items[1].find("#") == -1 else None
            )
            # type
            if items[2].find("#") == -1:
                schemas_lessons[i - 1].type = delete_spaces(items[2])
            else:
                schemas_lessons[i - 1].type = None

            for time in TimeTemplate:
                if time["min"] <= schemas_lessons[i - 1].time_start <= time["max"]:
                    lessons["schedulet"][DayChanger[schemas_lesson_day[i - 1]]]["lessons"][time["lesson"]].append(
                        schemas_lessons[i - 1])
                    break
    return lessons


def check_date(date_start: Union[str, None] = None, date_end: Union[str, None] = None):
    today = datetime.date.today()
    if date_start is not None and date_end is not None:
        date_start = datetime.datetime.strptime(date_start, "%d.%m.%Y")
        date_end = datetime.datetime.strptime(date_end, "%d.%m.%Y")
        return date_start <= datetime.datetime(day=today.day, month=today.month, year=today.year) <= date_end
    if date_start is not None:
        date_start = datetime.datetime.strptime(date_start, "%d.%m.%Y")
        return date_start == datetime.datetime(day=today.day, month=today.month, year=today.year)
    return True


def delete_spaces(string: str):
    res = "".join(f"{item} " for item in string.split() if len(item) > 0)
    return res[:-1]


def output_From_DBGroups(db_groups: list):
    groups = []
    for db_group in db_groups:
        schemas_group = schemas.GroupOutput(item=db_group)
        groups.append(schemas_group)
    return {"groups": groups}


def output_From_DBTeacher(db_teacher, dest='en'):
    if dest != 'ru':
        trans = tr.translate(db_teacher.translate_str()).split(" _ ")
        db_teacher.name = trans[0]
        db_teacher.fullname = trans[1]
        db_teacher.online_url = trans[2]
        db_teacher.alt_online_url = trans[3]
    return schemas.TeacherOutput(item=db_teacher)
