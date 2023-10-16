from sqlalchemy.orm import Session
from FastAPI_SQLAlchemy._fastapi_.db import schemas, models
from FastAPI_SQLAlchemy._fastapi_ import crud
from FastAPI_SQLAlchemy.parsing import schedule_parser as sp
from FastAPI_SQLAlchemy.parsing.config import settings

import json
import os

DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
AC_TYPES = ["Бакалавриат", "Специалитет", "Магистратура", "Аспирантура", "ПФ"]


def schedule_info_to_db(db: Session):
    types = sp.getAcademicTypes()
    for ac_type in types:
        filename = f"FastAPI_SQLAlchemy/parsing/schedule/{ac_type}.json"
        if os.path.exists(filename):
            with open(filename, "r", encoding='utf-8') as fp:
                print(f"Filename: {filename}")
                dict_json = json.loads(fp.read().replace("'", '"'))
                for course in dict_json["courses"]:
                    print("   course: " + course["name"])
                    for group in course["groups"]:
                        print("      group: " + group["name"])
                        db_group = schemas.GroupCreate
                        db_group.course = course["name"]
                        db_group.name = group["name"]
                        db_group.academic_name = ac_type

                        if not crud.get_group_by_Name(db, db_group.name):
                            crud.create_group(db, db_group)

                        for day in group["lessons"]:
                            for lessons in group["lessons"][day]:
                                for lesson in lessons["lessons"]:
                                    db_lesson = schemas.LessonCreate
                                    db_lesson.time_start = lessons["time_start"]
                                    db_lesson.time_end = lessons["time_end"]
                                    db_lesson.dot = lesson["dot"]
                                    db_lesson.cabinet = lesson["cabinet"]
                                    db_lesson.type = lesson["lesson_type"]
                                    db_lesson.weeks = lesson["weeks"]
                                    db_lesson.name = lesson["lesson_name"]
                                    db_lesson.subgroup = lesson["subgroup"]
                                    db_lesson.date_start = lesson["date_start"]
                                    db_lesson.date_end = lesson["date_end"]
                                    db_lesson.group_name = group["name"]
                                    db_lesson.day = day

                                    if crud.get_lesson(db, time_start=db_lesson.time_start,
                                                       time_end=db_lesson.time_end,
                                                       weeks=db_lesson.weeks,
                                                       date_start=db_lesson.date_start,
                                                       date_end=db_lesson.date_end,
                                                       day=db_lesson.day,
                                                       group_name=db_lesson.group_name,
                                                       name=db_lesson.name) is None:
                                        crud.create_lesson(db, db_lesson)
                                    else:
                                        crud.update_lesson(db=db,
                                                           time_start=db_lesson.time_start,
                                                           time_end=db_lesson.time_end,
                                                           dot=db_lesson.dot,
                                                           cabinet=db_lesson.cabinet,
                                                           type_=db_lesson.type,
                                                           weeks=db_lesson.weeks,
                                                           name=db_lesson.name,
                                                           subgroup=db_lesson.subgroup,
                                                           date_start=db_lesson.date_start,
                                                           date_end=db_lesson.date_end,
                                                           group_name=db_lesson.group_name,
                                                           day=db_lesson.day)

                                    for teacher_name in lesson["teacher_name"]:
                                        db_teacher = schemas.TeacherCreate(teacher_name, "", "", "")
                                        if db_teacher.name is not None:
                                            if crud.get_teacher_by_Name(db, db_teacher.name) is None:
                                                crud.create_teacher(db, db_teacher)

                                        db_lesson_teacher = schemas.LessonTeacherCreate
                                        db_lesson_teacher.teacher_id = crud.get_teacher_by_Name(db, teacher_name=teacher_name).id
                                        db_lesson_teacher.lesson_id = crud.get_lesson(db,
                                                                                      time_start=db_lesson.time_start,
                                                                                      time_end=db_lesson.time_end,
                                                                                      weeks=db_lesson.weeks,
                                                                                      date_start=db_lesson.date_start,
                                                                                      date_end=db_lesson.date_end,
                                                                                      day=db_lesson.day,
                                                                                      group_name=db_lesson.group_name,
                                                                                      name=db_lesson.name).id

                                        if crud.get_lesson_teacher(db, lesson_id=db_lesson_teacher.lesson_id,
                                                                   teacher_id=db_lesson_teacher.teacher_id) is None:
                                            crud.create_lesson_teacher(db, db_lesson_teacher)


def teachers_fullname_to_db(db: Session):
    if os.path.exists(settings.TEACHERS_FULLNAME_PATH):
        with open(settings.TEACHERS_FULLNAME_PATH, mode='r', encoding='utf-8') as fp:
            dict_json = json.load(fp)
            for fullname in dict_json['teachers_fullname']:
                buffer = fullname.split()
                if len(buffer) == 2:
                    shortname = f"{buffer[0]} {buffer[1][0]}."
                else:
                    shortname = f"{buffer[0]} {buffer[1][0]}.{buffer[2][0]}."
                crud.update_teacher(db, old_shortname=shortname, fullname=fullname)


def news_info_to_db(db: Session):
    preview = os.listdir(PREVIEW_DIR)
    news = os.listdir(NEWS_DIR)
    for i in range(len(news), 0, -1):
        if crud.get_news(db, pathToPreview=PREVIEW_DIR + str(i) + ".json",
                         pathToNews=NEWS_DIR + str(i) + ".json") is None:
            db_news = schemas.NewsCreate
            db_news.pathToPreview = PREVIEW_DIR + str(i) + ".json"
            db_news.pathToNews = NEWS_DIR + str(i) + ".json"
            crud.create_news(db, db_news)
    diff = len(preview) - len(news)
    if diff > 0:
        for i in range(len(preview), len(preview) - diff, -1):
            os.remove(PREVIEW_DIR + str(i) + ".json")


def idInverter(_id_: int):
    news = os.listdir(NEWS_DIR)
    print(f"_id_ = {_id_}\nnew _id_ = {len(news) - _id_ + 1}")
    return len(news) - _id_ + 1
