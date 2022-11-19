from sqlalchemy.orm import Session
from .db import models, schemas


def create_group(db: Session, group: schemas.GroupCreate):
    db_group = models.Group(name=group.name, course=group.course, academic_name=group.academic_name)
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def create_teacher(db: Session, teacher: schemas.TeacherCreate):
    db_teacher = models.Teacher(name=teacher.name, fullname=teacher.fullname, online_url=teacher.online_url,
                                alt_online_url=teacher.alt_online_url)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


def create_lesson(db: Session, lesson: schemas.LessonCreate):
    db_lesson = models.Lesson(
        time_start=lesson.time_start,
        time_end=lesson.time_end,
        dot=lesson.dot,
        cabinet=lesson.cabinet,
        type=lesson.type,
        weeks=lesson.weeks,
        name=lesson.name,
        subgroup=lesson.subgroup,
        date_start=lesson.date_start,
        date_end=lesson.date_end,
        day=lesson.day,
        group_name=lesson.group_name
    )
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson


def create_lesson_teacher(db: Session, lesson_teacher: schemas.LessonTeacher):
    db_lesson_teacher = models.LessonTeacher(lesson_id=lesson_teacher.lesson_id, teacher_id=lesson_teacher.teacher_id)
    db.add(db_lesson_teacher)
    db.commit()
    db.refresh(db_lesson_teacher)
    return db_lesson_teacher


def create_news(db: Session, news: schemas.NewsCreate):
    db_news = models.News(pathToNews=news.pathToNews, pathToPreview=news.pathToPreview)
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    return db_news


# Read
def get_group_by_Name(db: Session, group_name: str):
    return db.query(models.Group).filter(models.Group.name == group_name).first()


def get_groups_by_Course(db: Session, course: int):
    return db.query(models.Group).filter(models.Group.course == course).all()


def get_all_groups(db: Session):
    res = []
    for element in db.query(models.Group).all():
        res.append(element.name)
    return res


def get_groups_by_CourseAndAcType(db: Session, course: int, acType: str):
    return db.query(models.Group).filter(models.Group.course == course, models.Group.academic_name == acType).all()


def get_teacher_by_Name(db: Session, teacher_name: str):
    return db.query(models.Teacher).filter(models.Teacher.name == teacher_name).first()


def get_all_teachers(db: Session):
    res = []
    for elem in db.query(models.Teacher).all():
        res.append(elem.name)
    return res


def get_lessons_by_Day(db: Session, day: str):
    return db.query(models.Lesson).filter(models.Lesson.day == day).all()


def get_lessons_by_TeacherName(db: Session, teacher_name: str):
    teacher = db.query(models.Teacher).filter(models.Teacher.name == teacher_name).first()
    res = []
    for item in db.query(models.LessonTeacher).filter(models.LessonTeacher.teacher_id == teacher.id).all():
        res.append(db.query(models.Lesson).filter(models.Lesson.id == item.lesson_id).first())
    return res


def get_lessons_by_GroupName(db: Session, group_name: str):
    return db.query(models.Lesson).filter(models.Lesson.group_name == group_name).all()


def get_lessons_by_DayAndGroupName(db: Session, group_name: str, day: str):
    return db.query(models.Lesson).filter(models.Lesson.group_name == group_name, models.Lesson.day == day).all()


def get_lesson(db: Session,
               time_start: str,
               time_end: str,
               weeks: str,
               date_start: str,
               date_end: str,
               day: str,
               group_name: str,
               name: str):
    return db.query(models.Lesson).filter(models.Lesson.time_start == time_start,
                                          models.Lesson.time_end == time_end,
                                          models.Lesson.weeks == weeks,
                                          models.Lesson.date_start == date_start,
                                          models.Lesson.date_end == date_end,
                                          models.Lesson.day == day,
                                          models.Lesson.group_name == group_name,
                                          models.Lesson.name == name).first()


def get_lesson_teacher(db: Session, lesson_id: int, teacher_id: int):
    return db.query(models.LessonTeacher).filter(models.LessonTeacher.teacher_id == teacher_id,
                                                 models.LessonTeacher.lesson_id == lesson_id).first()


def get_news_by_Id(db: Session, _id_: int):
    return db.query(models.News).filter(models.News.id == _id_).first()


def get_news(db: Session, pathToPreview: str, pathToNews: str):
    return db.query(models.News).filter(models.News.pathToPreview == pathToPreview,
                                        models.News.pathToNews == pathToNews).first()


# Update
def update_group(db: Session, old_name: str, new_name: str = None, new_course: int = None,
                 new_academic_name: str = None):
    db_group = get_group_by_Name(db, old_name)
    if new_name is not None:
        db_group.name = new_name
    if new_course is not None:
        db_group.course = new_course
    if new_academic_name is not None:
        db_group.academic_name = new_academic_name
    db.commit()
    db.refresh(db_group)
    return db_group


def update_teacher(db: Session, old_shortname: str, shortname: str = None, fullname: str = None, online_url: str = None,
                   alt_online_url: str = None):
    db_teacher = get_teacher_by_Name(db, old_shortname)
    if db_teacher is None:
        return None
    if shortname is not None:
        db_teacher.name = shortname
    if fullname is not None:
        db_teacher.fullname = fullname
    if online_url is not None:
        db_teacher.online_url = online_url
    if alt_online_url is not None:
        db_teacher.alt_online_url = alt_online_url
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


def update_lesson(db: Session,
                  time_start: str = None,
                  time_end: str = None,
                  dot: str = None,
                  cabinet: str = None,
                  type_: bool = None,
                  weeks: str = None,
                  name: str = None,
                  subgroup: str = None,
                  date_start: str = None,
                  date_end: str = None,
                  day: str = None,
                  group_name: str = None):
    db_lesson = get_lesson(db=db,
                           time_start=time_start,
                           time_end=time_end,
                           weeks=weeks,
                           date_start=date_start,
                           date_end=date_end,
                           day=day,
                           group_name=group_name,
                           name=name)
    if time_start is not None:
        db_lesson.time_start = time_start
    if time_end is not None:
        db_lesson.time_end = time_end
    if dot is not None:
        db_lesson.dot = dot
    if cabinet is not None:
        db_lesson.cabinet = cabinet
    if type_ is not None:
        db_lesson.type_ = type_
    if weeks is not None:
        db_lesson.weeks = weeks
    if name is not None:
        db_lesson.name = name
    if subgroup is not None:
        db_lesson.subgroup = subgroup
    if date_start is not None:
        db_lesson.date_start = date_start
    if date_end is not None:
        db_lesson.date_end = date_end
    if day is not None:
        db_lesson.day = day
    if group_name is not None:
        db_lesson.group_name = group_name

    db.commit()
    db.refresh(db_lesson)
    return db_lesson


# Delete
def delete_group_by_Id(db: Session, group_name: int):
    group = get_group_by_Id(db, group_name)
    lessons = get_lessons_by_GroupId(db, group.id)
    for lesson in lessons:
        db.delete(lesson)
    db.delete(group)
    db.commit()
    return group


def delete_group_by_Name(db: Session, group_name: str):
    group = get_group_by_Name(db, group_name)
    lessons = get_lessons_by_GroupId(db, group.id)
    for lesson in lessons:
        db.delete(lesson)
    db.delete(group)
    db.commit()
    return group


def delete_teacher_by_Name(db: Session, teacher_name: str):
    teacher = get_teacher_by_Name(db, teacher_name)
    lessons = get_lessons_by_TeacherName(db, teacher_name)
    for lesson in lessons:
        db.delete(lesson)
    db.delete(teacher)
    db.commit()
    return teacher


def delete_lessons_by_GroupId(db: Session, group_name: int):
    lessons = get_lessons_by_GroupId(db, group_name)
    for lesson in lessons:
        db.delete(lesson)
    db.commit()
    return group


def delete_lessons_by_Day(db: Session, day: str):
    lessons = get_lessons_by_Day(db, day)
    for lesson in lessons:
        db.delete(lesson)
    db.commit()
    return group


def delete_lessons_by_DayAndGroupId(db: Session, group_name: int, day: str):
    lessons = get_lessons_by_DayAndGroupId(db, group_name, day)
    for lesson in lessons:
        db.delete(lesson)
    db.commit()
    return group
