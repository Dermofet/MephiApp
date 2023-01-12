from typing import List, Optional, Union

from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session

from backend.Schemas.Group import GroupOutput
from backend.Schemas.LessonTranslate import LessonTranslateOutput
from backend.Schemas.Room import RoomOutput
from backend.Schemas.Teacher import TeacherOutput


class LessonBase(BaseModel):
    time_start: Optional[str] = Field(description="Время начала занятия")
    time_end: Optional[str] = Field(description="Время конец занятия")
    dot: Optional[bool] = Field(description="Динстанционное ли занятие")
    weeks: Optional[int] = Field(description="Недели, в которые проводится занятие. 0 - четные, 1 - нечетные, 2 - все")
    day: Optional[str] = Field(description="День недели")
    date_start: Optional[str] = Field(description="Дата начала занятия")
    date_end: Optional[str] = Field(description="Дата конца занятия")


class LessonCreate(LessonBase):
    type: Optional[str] = Field(description="Тип занятия")
    name: Optional[str] = Field(description="Название занятия")
    subgroup: Optional[str] = Field(description="Подгруппа, у которой проводится занятие")
    group: Optional[str] = Field(description="Группа, у которой проводится занятие")
    course: Optional[str] = Field(description="Курс обученя")
    room: Optional[str] = Field(description="Аудитория в которой проводится занятие")
    academic: Optional[str] = Field(description="Ученое звание")
    teacher_name: Optional[str] = Field(description="Имя преподавателя")
    lang: Optional[str] = Field(description="Язык (для перевода)")


class LessonOutputFromDB(LessonBase):
    groups: Optional[List[GroupOutput]] = Field(description="Список групп, которые находятся на занятии")
    teachers: Optional[List[TeacherOutput]] = Field(description="Список преподавателей, которые находятся на занятии")
    rooms: Optional[List[RoomOutput]] = Field(description="Список аудиторий, в которой проводится занятие")
    trans: Optional[LessonTranslateOutput] = Field(description="Переведенные поля модели")

    class Config:
        orm_mode = True


class LessonOutput(LessonBase):
    groups: Optional[List[GroupOutput]] = Field(description="Список групп, которые находятся на занятии")
    teachers: Optional[List[TeacherOutput]] = Field(description="Список преподавателей, которые находятся на занятии")
    rooms: Optional[List[RoomOutput]] = Field(description="Список аудиторий, в которой проводится занятие")
    trans: Optional[LessonTranslateOutput] = Field(description="Переведенные поля модели")
    weeks: List[int] = Field(description="Недели, в которые проводится занятие")


class Lesson(LessonBase):
    guid: UUID4 = Field(description="ID")
    groups: List[GroupOutput] = Field(description="Список групп, которые находятся на занятии")
    teachers: List[TeacherOutput] = Field(description="Список преподавателей, которые находятся на занятии")
    rooms: List[RoomOutput] = Field(description="Список аудиторий, в которой проводится занятие")
    trans: LessonTranslateOutput = Field(description="Переведенные поля модели")

    class Config:
        orm_mode = True
