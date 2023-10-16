from sqlalchemy.orm import Session
from pydantic import BaseModel, HttpUrl, Field
from typing import Union
import collections

from FastAPI_SQLAlchemy._fastapi_.db import models
from FastAPI_SQLAlchemy.translator import translator as tr


# Group
class GroupBase(BaseModel):
    name: Union[str, None] = None
    course: Union[int, None] = None
    academic_name: Union[str, None] = None


class GroupCreate(GroupBase):
    pass


class GroupOutput(GroupBase):
    def __init__(self, item: models.Group):
        super().__init__()
        self.name = item.name
        self.course = item.course
        self.academic_name = item.academic_name


class Group(GroupBase):
    id: int

    class Config:
        orm_mode = True


# Teacher
class TeacherBase(BaseModel):
    name: Union[str, None] = None
    fullname: Union[str, None] = None
    online_url: Union[str, None] = None
    alt_online_url: Union[str, None] = None


class TeacherCreate(TeacherBase):
    def __init__(self, name: str, fullname: str, online_url: str, alt_online_url: str):
        super().__init__()
        self.name = name
        self.fullname = fullname
        self.online_url = online_url
        self.alt_online_url = alt_online_url


class TeacherOutput(TeacherBase):
    def __init__(self, item: models.Teacher):
        super().__init__()
        self.name = item.name
        self.fullname = item.fullname
        self.online_url = item.online_url
        self.alt_online_url = item.alt_online_url

    def translate_str(self):
        return f"{self.name} _ {self.fullname} _ {self.online_url} _ {self.alt_online_url}"


class Teacher(TeacherBase):
    class Config:
        orm_mode = True


# Lesson
class LessonBase(BaseModel):
    time_start: Union[str, None] = None
    time_end: Union[str, None] = None
    dot: Union[bool, None] = None
    cabinet: Union[str, None] = None
    type: Union[str, None] = None
    weeks: Union[list[int], None] = None
    name: Union[str, None] = None
    subgroup: Union[str, None] = None


class LessonCreate(LessonBase):
    day: Union[str, None] = None
    date_start: Union[str, None] = None
    date_end: Union[str, None] = None


class LessonOutput(LessonBase):
    teacher_name: Union[list[str], None] = None
    teacher_fullname: Union[list[str], None] = None
    tr_teacher_name: Union[list[str], None] = None
    tr_teacher_fullname: Union[list[str], None] = None

    def __init__(self, item: models.Lesson, db: Session):
        super().__init__()
        self.time_start = item.time_start
        self.time_end = item.time_end
        self.dot = item.dot
        self.cabinet = item.cabinet
        self.type = item.type
        if item.weeks == "еженед":
            self.weeks = list(range(1, 17))
        elif item.weeks == "чет":
            self.weeks = list(range(2, 17, 2))
        else:
            self.weeks = list(range(1, 16, 2))
        self.name = item.name
        self.subgroup = item.subgroup
        teachers = item.teachers(db)
        self.teacher_name = [TeacherOutput(teacher).name for teacher in teachers]
        self.teacher_fullname = [TeacherOutput(teacher).fullname for teacher in teachers]
        self.tr_teacher_name = []
        self.tr_teacher_fullname = []

    def translate_str(self):
        type_ = "#"
        if self.type == 'Лаб':
            type_ = "Лабораторная работа"

        elif self.type == 'Лек':
            type_ = "Лекция"
        elif self.type == 'Пр':
            type_ = "Практика"
        # trans = name + teacher_name + teacher_fullname + subgroup + type
        #     # = None
        if self.subgroup is None:
            if len(self.teacher_name) == 0:
                return (
                    f"{self.name} + # + # + # + {type_} | "
                    if len(self.teacher_fullname) == 0
                    else f'{self.name} + # + {" _ ".join(self.teacher_fullname)} + # + {type_} | '
                )
            else:
                return (
                    f'{self.name} + {" _ ".join(self.teacher_name)} + # + # + {type_} | '
                    if len(self.teacher_fullname) == 0
                    else f'{self.name} + {" _ ".join(self.teacher_name)} + {" _ ".join(self.teacher_fullname)} + # + {type_} | '
                )
        elif len(self.teacher_name) == 0:
            if len(self.teacher_fullname) == 0:
                return f"{self.name} + # + # + {self.subgroup} + {type_} | "
            else:
                return f'{self.name} + # + {" _ ".join(self.teacher_fullname)} + {self.subgroup} + {type_} | '
        elif len(self.teacher_fullname) == 0:
            return f'{self.name} + {" _ ".join(self.teacher_name)} + # + {self.subgroup} + {type_} | '
        else:
            return f'{self.name} + {" _ ".join(self.teacher_name)} + {" _ ".join(self.teacher_fullname)} + {self.subgroup} + {type_} | '


class LessonOutputT(LessonBase):
    group_name: Union[list[str], None] = None

    def __init__(self, item: models.Lesson, db: Session):
        super().__init__()
        self.time_start = item.time_start
        self.time_end = item.time_end
        self.dot = item.dot
        self.cabinet = item.cabinet
        self.type = item.type
        if item.weeks == "еженед":
            self.weeks = list(range(1, 17))
        elif item.weeks == "чет":
            self.weeks = list(range(2, 17, 2))
        else:
            self.weeks = list(range(1, 16, 2))
        self.name = item.name
        self.subgroup = item.subgroup
        self.group_name = list(item.groups(db))

    def translate_str(self):
        type_ = "#"
        if self.type == 'Лаб':
            type_ = "Лабораторная работа"

        elif self.type == 'Лек':
            type_ = "Лекция"
        elif self.type == 'Пр':
            type_ = "Практика"
        # trans = name + subgroup + type
        if self.subgroup is None:
            return f"{self.name} + # + {type_} | "
        else:
            return f"{self.name} + {self.subgroup} + {type_} | "


class Lesson(LessonBase):
    id: int
    day: Union[str, None] = None
    group_name: Union[str, None] = None
    date_start: Union[str, None] = None
    date_end: Union[str, None] = None

    class Config:
        orm_mode = True


class LessonTeacherBase(BaseModel):
    teacher_id: Union[int, None] = None
    lesson_id: Union[int, None] = None


class LessonTeacherCreate(LessonTeacherBase):
    pass


class LessonTeacherOutput(LessonTeacherBase):
    def __init__(self, item: models.LessonTeacher):
        super().__init__()
        self.lesson_id = item.lesson_id
        self.teacher_id = item.teacher_id


class LessonTeacher(LessonTeacherBase):
    class Config:
        orm_mode = True


class NewsBase(BaseModel):
    pathToPreview: Union[str, None] = None
    pathToNews: Union[str, None] = None


class NewsCreate(NewsBase):
    pass


class NewsOutput(NewsBase):
    pass


class News(NewsBase):
    id: int

    class Config:
        orm_mode = True
