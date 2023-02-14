from copy import deepcopy
from typing import List, Optional, Union

from pydantic import UUID4, BaseModel, Field, validator
from sqlalchemy.orm import Session

from backend.schemas.group import GroupOutputSchema, GroupSchema
from backend.schemas.lesson_translate import LessonTranslateSchema
from backend.schemas.room import RoomOutputSchema, RoomSchema
from backend.schemas.teacher_translate import TeacherTranslateOutputSchema, TeacherTranslateSchema


class LessonBaseSchema(BaseModel):
    time_start: str = Field(description="Время начала занятия")
    time_end: str = Field(description="Время конец занятия")
    dot: bool = Field(description="Динстанционное ли занятие")
    weeks: int = Field(description="Недели, в которые проводится занятие. 0 - четные, 1 - нечетные, 2 - все")
    day: str = Field(description="День недели")
    date_start: Optional[str] = Field(description="Дата начала занятия")
    date_end: Optional[str] = Field(description="Дата конца занятия")


class LessonCreateSchema(LessonBaseSchema):
    type: Optional[str] = Field(description="Тип занятия")
    name: str = Field(description="Название занятия")
    subgroup: Optional[str] = Field(description="Подгруппа, у которой проводится занятие")
    group: str = Field(description="Группа, у которой проводится занятие")
    course: str = Field(description="Курс обученя")
    room: Optional[str] = Field(description="Аудитория в которой проводится занятие")
    academic: str = Field(description="Ученое звание")
    teacher_name: str = Field(description="Имя преподавателя")
    lang: str = Field(description="Язык (для перевода)")

    @validator("teacher_name", pre=True)
    def none_teacher(cls, value):
        if isinstance(value, type(None)):
            return "None"
        elif isinstance(value, str):
            return value
        else:
            raise ValueError('Имя преподавателя не строка')


class LessonOutputBaseSchema(LessonBaseSchema):
    groups: list[GroupSchema] = Field(default=[], description="Список групп, которые находятся на занятии")
    teachers: list[TeacherTranslateSchema] = Field(default=[], description="Список преподавателей, которые находятся на занятии")
    rooms: list[RoomSchema] = Field(default=[], description="Список аудиторий, в которой проводится занятие")

    @validator("teachers", pre=True)
    def none_teacher(cls, values):
        res = []
        for value in values:
            for trans in value.trans:
                if trans.name != 'None':
                    res.append(trans)
        return res

    class Config:
        orm_mode = True


class LessonOutputSchema(LessonOutputBaseSchema):
    guid: UUID4 = Field(description="ID")
    weeks: list[int] = Field(description="Недели, в которые проводится занятие")
    trans: list[TeacherTranslateOutputSchema] = Field(default=[], description="Список полей, нуждающихся в переводе, на разных языках")

    @validator("weeks", pre=True)
    def change_weeks(cls, value):
        if isinstance(value, int):
            if value == 0:
                return [x for x in range(2, 16, 2)]
            elif value == 1:
                return [x for x in range(1, 15, 2)]
            elif value == 2:
                return [x for x in range(1, 16)]
        elif isinstance(value, list):
            return value
        else:
            raise ValueError('Неверное значение для weeks. Оно может быть 0 - четные недели, 1 - нечетные недели, '
                             '2 - все недели.')


class LessonSchema(LessonOutputBaseSchema):
    guid: UUID4 = Field(description="ID")
    trans: list[LessonTranslateSchema] = Field(default=[], description="Список полей, нуждающихся в переводе, на разных языках")

    class Config:
        orm_mode = True
