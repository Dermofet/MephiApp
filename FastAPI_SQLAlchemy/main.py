import json
import logging
import time
import types

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import uvicorn

from ._fastapi_ import response_detail as rd
from ._fastapi_ import crud
from ._fastapi_.db import models, schemas
from ._fastapi_.db.database import SessionLocal, engine
from ._fastapi_ import tools

from FastAPI_SQLAlchemy.parsing import input_parse_info
from FastAPI_SQLAlchemy.parsing import schedule_parser as sp
from FastAPI_SQLAlchemy.parsing import news_parser as np

from .translator import translator as tr

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
logFilename = "FastAPI_SQLAlchemy/logs/log1"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


logging.basicConfig(filename=logFilename, level=logging.INFO, format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')


@app.get("/")
async def main():
    logging.info("API: main | --status: Get request")
    logging.info("API: main | --status: Status_code = 200")
    return "It's host for MEPhI app. To check the api, please, idite nahui!!!"


@app.get("/all_lessons_by_group/", response_model=dict)
async def get_lessons_by_group(group_name: str, lang: str = 'ru', db: Session = Depends(get_db)):
    try:
        logging.info("API: get_lessons_by_group | --args: {} | --status: Get requests".format(group_name))
        db_lessons = crud.get_lessons_by_GroupName(db, group_name)
        if len(db_lessons) == 0:
            logging.error("API: get_lessons_by_group | --args: {} | --status: Status_code = 406".format(group_name))
            raise HTTPException(status_code=406, detail=rd.unexpected_parameters_406)
        lessons = {"group": group_name} | tools.output_From_DBLesson(db_lessons, db=db, dest=lang)
        logging.info("API: get_lessons_by_group | --args: {} | --status: Status_code = 200".format(group_name))
        return lessons
    except (Exception,) as err:
        logging.exception(err)
        logging.info("API: get_lessons_by_group | --args: {} | --status: Status_code = 500".format(group_name))
        raise HTTPException(status_code=500, detail=rd.server_error_500)


@app.get("/all_lessons_by_group_and_day/", response_model=dict)
async def get_lessons_by_group_day(group_name: str, day: str, lang: str = 'ru', db: Session = Depends(get_db)):
    try:
        logging.info("API: get_lessons_by_group_day | --args: {}, {} | --status: Get request".format(group_name, day))
        db_lessons = crud.get_lessons_by_DayAndGroupName(db, group_name, day)
        if len(db_lessons) == 0:
            logging.error(
                "API: get_lessons_by_group_day | --args: {}, {} | --status: Status_code = 406".format(group_name, day))
            raise HTTPException(status_code=406, detail=rd.unexpected_parameters_406)
        lessons = {"group": group_name} | tools.output_From_DBLesson(db_lessons, db=db, dest=lang)
        logging.info(
            "API: get_lessons_by_group_day | --args: {}, {} | --status: Status_code = 200".format(group_name, day))
        return lessons
    except (Exception,) as err:
        logging.exception(err)
        logging.info(
            "API: get_lessons_by_group_day | --args: {}, {} | --status: Status_code = 500".format(group_name, day))
        raise HTTPException(status_code=500, detail=rd.server_error_500)


@app.get("/all_lessons_by_teacher/", response_model=dict)
async def get_lessons_by_teacher(teacher_name: str, lang: str = 'ru', db: Session = Depends(get_db)):
    try:
        logging.info("API: get_lessons_by_teacher | --args: {} | --status: Get request".format(teacher_name))
        db_lessons = crud.get_lessons_by_TeacherName(db, teacher_name=teacher_name)
        if len(db_lessons) == 0:
            logging.error("API: get_lessons_by_teacher | --args: {} | --status: Status_code = 406".format(teacher_name))
            raise HTTPException(status_code=406, detail=rd.unexpected_parameters_406)
        res = {"teachers": teacher_name,
               "tr_teachers": tr.translate(teacher_name, dest=lang),
               "tr_teachers_fullname": tr.translate(crud.get_teacher_by_Name(db, teacher_name).fullname, dest=lang)} \
            | tools.output_From_DBLessonT(db_lessons, db=db, dest=lang)
        logging.info("API: get_lessons_by_teacher | --args: {} | --status: Status_code = 200".format(teacher_name))
        return res
    except (Exception,) as err:
        logging.exception(err)
        logging.info("API: get_lessons_by_teacher | --args: {} | --status: Status_code = 500".format(teacher_name))
        raise HTTPException(status_code=500, detail=rd.server_error_500)


@app.get("/teacher_info/")
async def get_teacher_info(teacher_name: str, lang: str = 'ru', db: Session = Depends(get_db)):
    try:
        logging.info("API: get_teacher_info | --args: {} | --status: Get request".format(teacher_name))
        db_teacher = crud.get_teacher_by_Name(db, teacher_name=teacher_name)
        if db_teacher is None:
            logging.error("API: get_teacher_info | --args: {} | --status: Status_code = 406".format(teacher_name))
            raise HTTPException(status_code=406, detail=rd.unexpected_parameters_406)
        res = tools.output_From_DBTeacher(db_teacher, dest=lang)
        logging.info("API: get_lessons_by_teacher | --args: {} | --status: Status_code = 200".format(teacher_name))
        return res
    except (Exception,) as err:
        logging.exception(err)
        logging.info("API: get_lessons_by_teacher | --args: {} | --status: Status_code = 500".format(teacher_name))
        raise HTTPException(status_code=500, detail=rd.server_error_500)


@app.get("/all_groups_by_course/", response_model=dict[str, list[schemas.GroupOutput]])
async def get_groups_by_course(course: int, db: Session = Depends(get_db)):
    try:
        logging.info("API: get_groups_by_course | --args: {} | --status: Get request".format(course))
        db_groups = crud.get_groups_by_Course(db, course=course)
        if len(db_groups) == 0:
            logging.error("API: get_groups_by_course | --args: {} | --status: Status_code = 406".format(course))
            raise HTTPException(status_code=406, detail=rd.unexpected_parameters_406)
        logging.info("API: get_groups_by_course | --args: {} | --status: Status_code = 200".format(course))
        return tools.output_From_DBGroups(db_groups)
    except (Exception,) as err:
        logging.exception(err)
        logging.info("API: get_groups_by_course | --args: {} | --status: Status_code = 500".format(course))
        raise HTTPException(status_code=500, detail=rd.server_error_500)


@app.get("/all_groups_by_course_acType/", response_model=dict[str, list[schemas.GroupOutput]])
async def get_groups_by_course_acType(course: int, acType: str, db: Session = Depends(get_db)):
    try:
        logging.info("API: get_groups_by_course_acType | --args: {}, {} | --status: Get request".format(course, acType))
        db_groups = crud.get_groups_by_CourseAndAcType(db, course=course, acType=acType)
        if len(db_groups) == 0:
            logging.error(
                "API: get_groups_by_course_acType | --args: {}, {} | --status: Status_code = 406".format(course,
                                                                                                         acType))
            raise HTTPException(status_code=406, detail=rd.unexpected_parameters_406)
        logging.info(
            "API: get_groups_by_course_acType | --args: {}, {} | --status: Status_code = 200".format(course, acType))
        return tools.output_From_DBGroups(db_groups)
    except (Exception,) as err:
        logging.exception(err)
        logging.info(
            "API: get_groups_by_course_acType | --args: {}, {} | --status: Status_code = 500".format(course, acType))
        raise HTTPException(status_code=500, detail=rd.server_error_500)


@app.get("/all_groups/")
async def get_all_groups(db: Session = Depends(get_db)):
    try:
        logging.info("API: get_all_groups | --status: Get request")
        db_groups = crud.get_all_groups(db)
        if len(db_groups) == 0:
            logging.error("API: get_all_groups | --status: Status_code = 406")
            raise HTTPException(status_code=406, detail=rd.unexpected_parameters_406)
        logging.info("API: get_all_groups | --status: Status_code = 200")
        return {"groups": db_groups}
    except (Exception,) as err:
        logging.exception(err)
        logging.info("API: get_all_groups | --status: Status_code = 500")
        raise HTTPException(status_code=500, detail=rd.server_error_500)


@app.get("/all_teachers/")
async def get_all_teachers(lang: str = 'ru', db: Session = Depends(get_db)):
    try:
        logging.info("API: get_all_teachers | --status: Get request")
        db_teachers = crud.get_all_teachers(db)
        if len(db_teachers) == 0:
            logging.error("API: get_all_teachers | --status: Status_code = 406")
            raise HTTPException(status_code=406, detail=rd.unexpected_parameters_406)
        logging.info("API: get_all_teachers | --status: Status_code = 200")
        db_teachers.sort()
        return {"teachers": tr.translate(" | ".join(db_teachers), dest=lang).split(" | ")}
    except (Exception,) as err:
        logging.exception(err)
        logging.info("API: get_all_teachers | --status: Status_code = 500")
        raise HTTPException(status_code=500, detail=rd.server_error_500)


@app.get("/news_preview_by_id/")
async def get_news_preview_by_id(_id_: int, db: Session = Depends(get_db)):
    try:
        logging.info("API: get_news_preview_by_id | --args: {} | --status: Get request".format(_id_))
        db_news = crud.get_news_by_Id(db, input_parse_info.idInverter(_id_))
        if db_news is None:
            logging.error("API: get_news_preview_by_id | --args: {} | --status: Status_code = 406".format(_id_))
            raise HTTPException(status_code=406, detail=rd.unexpected_parameters_406)
        logging.info("API: get_news_preview_by_id | --args: {} | --status: Status_code = 200".format(_id_))
        with open(db_news.pathToPreview, 'r', encoding='utf-8') as fp:
            return json.load(fp=fp)
    except (Exception,) as err:
        logging.exception(err)
        logging.info("API: get_news_preview_by_id | --args: {} | --status: Status_code = 500".format(_id_))
        raise HTTPException(status_code=500, detail=rd.server_error_500)


@app.get("/news_previews_by_id/")
async def get_news_previews_by_id(start: int, end: int, db: Session = Depends(get_db)):
    try:
        logging.info("API: get_news_previews_by_id | --args: {}, {} | --status: Get request".format(start, end))
        db_news = {"news": []}
        for _id_ in range(start, end):
            with open(crud.get_news_by_Id(db, input_parse_info.idInverter(_id_)).pathToPreview, 'r',
                      encoding='utf-8') as fp:
                db_news["news"].append(json.load(fp=fp))
        if len(db_news["news"]) == 0:
            logging.error(
                "API: get_news_previews_by_id | --args: {}, {} | --status: Status_code = 406".format(start, end))
            raise HTTPException(status_code=406, detail=rd.unexpected_parameters_406)
        logging.info("API: get_news_previews_by_id | --args: {}, {} | --status: Status_code = 200".format(start, end))
        return db_news
    except (Exception,) as err:
        logging.exception(err)
        logging.info("API: get_news_previews_by_id | --args: {}, {} | --status: Status_code = 500".format(start, end))
        raise HTTPException(status_code=500, detail=rd.server_error_500)


@app.get("/news_page_by_id/")
async def get_news_page_by_id(_id_: int, db: Session = Depends(get_db)):
    try:
        logging.info("API: get_news_page_by_id | --args: {} | --status: Get request".format(_id_))
        db_news = crud.get_news_by_Id(db, input_parse_info.idInverter(_id_))
        if db_news is None:
            logging.error("API: get_news_page_by_id | --args: {} | --status: Status_code = 406".format(_id_))
            raise HTTPException(status_code=406, detail=rd.unexpected_parameters_406)
        logging.info("API: get_news_page_by_id | --args: {} | --status: Status_code = 200".format(_id_))
        with open(db_news.pathToNews, 'r', encoding='utf-8') as fp:
            return json.load(fp=fp)
    except (Exception,) as err:
        logging.exception(err)
        logging.info("API: get_news_page_by_id | --args: {} | --status: Status_code = 500".format(_id_))
        raise HTTPException(status_code=500, detail=rd.server_error_500)


@app.get("/parsing_schedule/")
def parsing_schedule(schedule: bool = True, teacher: bool = True):
    try:
        logging.info(
            "API: parsing_schedule | --args: {}, {} | --status: Start parsing schedule".format(schedule, teacher))
        if schedule:
            sp.parse_schedule()
        if teacher:
            sp.parse_teachers_fullname()
        logging.info(
            "API: parsing_schedule | --args: {}, {} | --status: Successful parsing schedule".format(schedule, teacher))
    except (Exception,) as err:
        logging.exception(err)
        logging.info("API: parsing_schedule | --args: {}, {} | --status: Status_code = 500".format(schedule, teacher))
        raise HTTPException(status_code=500, detail=rd.server_error_500)


@app.get("/fill_db/")
def fill_db(schedule: bool = True, news: bool = True, teacher_fullname: bool = True, db: Session = Depends(get_db)):
    try:
        logging.info("API: fill_db | --args: {}, {}, {} | --status: Start filling db"
                     .format(schedule, news, teacher_fullname))
        if schedule:
            input_parse_info.schedule_info_to_db(db)
            logging.info("API: fill_db | --args: {}, {}, {} | --status: Successful filling schedule"
                         .format(schedule, news, teacher_fullname))
        if news:
            input_parse_info.news_info_to_db(db)
            logging.info("API: fill_db | --args: {}, {}, {} | --status: Successful filling news"
                         .format(schedule, news, teacher_fullname))
        if teacher_fullname:
            input_parse_info.teachers_fullname_to_db(db)
            logging.info("API: fill_db | --args: {}, {}, {} | --status: Successful filling teachers fullname"
                         .format(schedule, news, teacher_fullname))
        logging.info("API: fill_db | --status: Successful filling db")
    except (Exception,) as err:
        logging.exception(err)
        logging.info("API: fill_db | --status: Status_code = 500")
        raise HTTPException(status_code=500, detail=rd.server_error_500)


@app.get("/parsing_news/")
async def parsing_news():
    try:
        logging.info("API: parsing_news | --status: Start parsing news")
        np.parse()
        logging.info("API: parsing_news | --status: Successful parsing news")
    except (Exception,) as err:
        logging.exception(err)
        logging.info("API: parsing_news | --status: Status_code = 500")
        raise HTTPException(status_code=500, detail=rd.server_error_500)
