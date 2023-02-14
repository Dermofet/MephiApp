from copy import deepcopy
from typing import List, Optional, Union

from pydantic import UUID4, BaseModel, Field, validator
from sqlalchemy.orm import Session

from backend.schemas.group import GroupOutputSchema, GroupSchema
from backend.schemas.room import RoomOutputSchema, RoomSchema
from backend.schemas.teacher_translate import TeacherTranslateOutputSchema, TeacherTranslateSchema


class LessonWithoutLanguageBaseSchema(BaseModel):
    time_start: str = Field(description="Время начала занятия")
    time_end: str = Field(description="Время конец занятия")
    dot: bool = Field(description="Динстанционное ли занятие")
    weeks: int = Field(description="Недели, в которые проводится занятие. 0 - четные, 1 - нечетные, 2 - все")
    day: str = Field(description="День недели")
    date_start: Optional[str] = Field(description="Дата начала занятия")
    date_end: Optional[str] = Field(description="Дата конца занятия")


class LessonWithoutLanguageOutputSchema(LessonWithoutLanguageBaseSchema):
    groups: list[GroupOutputSchema] = Field(description="Список групп, которые находятся на занятии")
    teachers: list[TeacherTranslateOutputSchema] = Field(description="Список преподавателей, которые находятся на занятии")
    rooms: list[RoomOutputSchema] = Field(description="Список аудиторий, в которой проводится занятие")
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


class LessonWithoutLanguageSchema(LessonWithoutLanguageBaseSchema):
    guid: UUID4 = Field(description="ID")
    groups: list[GroupSchema] = Field(description="Список групп, которые находятся на занятии")
    teachers: list[TeacherTranslateSchema] = Field(description="Список преподавателей, которые находятся на занятии")
    rooms: list[RoomSchema] = Field(description="Список аудиторий, в которой проводится занятие")

    class Config:
        orm_mode = True
