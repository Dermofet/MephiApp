from typing import List, Optional, Union

from pydantic import UUID4, BaseModel, Field, validator
from sqlalchemy.orm import Session

from backend.Schemas.Group import Group, GroupOutput
from backend.Schemas.LessonTranslate import LessonTranslate, LessonTranslateOutput
from backend.Schemas.Room import Room, RoomOutput
from backend.Schemas.Teacher import Teacher, TeacherOutput


class LessonBase(BaseModel):
    time_start: str = Field(description="Время начала занятия")
    time_end: str = Field(description="Время конец занятия")
    dot: bool = Field(description="Динстанционное ли занятие")
    weeks: int = Field(description="Недели, в которые проводится занятие. 0 - четные, 1 - нечетные, 2 - все")
    day: str = Field(description="День недели")
    date_start: Optional[str] = Field(description="Дата начала занятия")
    date_end: Optional[str] = Field(description="Дата конца занятия")


class LessonCreate(LessonBase):
    type: str = Field(description="Тип занятия")
    name: str = Field(description="Название занятия")
    subgroup: Optional[str] = Field(description="Подгруппа, у которой проводится занятие")
    group: str = Field(description="Группа, у которой проводится занятие")
    course: str = Field(description="Курс обученя")
    room: str = Field(description="Аудитория в которой проводится занятие")
    academic: str = Field(description="Ученое звание")
    teacher_name: str = Field(description="Имя преподавателя")
    lang: str = Field(description="Язык (для перевода)")


class LessonOutput(LessonBase):
    guid: UUID4 = Field(description="ID")
    groups: list[GroupOutput] = Field(description="Список групп, которые находятся на занятии")
    teachers: list[TeacherOutput] = Field(description="Список преподавателей, которые находятся на занятии")
    rooms: list[RoomOutput] = Field(description="Список аудиторий, в которой проводится занятие")
    trans: List[LessonTranslate] = Field(description="Переведенные поля модели")
    weeks: list[int] = Field(description="Недели, в которые проводится занятие")

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


class Lesson(LessonBase):
    guid: UUID4 = Field(description="ID")
    groups: list[Group] = Field(description="Список групп, которые находятся на занятии")
    teachers: list[Teacher] = Field(description="Список преподавателей, которые находятся на занятии")
    rooms: list[Room] = Field(description="Список аудиторий, в которой проводится занятие")
    trans: List[LessonTranslate] = Field(description="Переведенные поля модели")

    class Config:
        orm_mode = True
