from datetime import date, time
from typing import List, Optional

from pydantic import Field, field_validator
from etl.schemas.base import Base


class LessonExtracting(Base):
    time_start: time = Field(description="Время начала занятия")
    time_end: time = Field(description="Время конец занятия")
    dot: bool = Field(description="Динстанционное ли занятие")
    weeks: Optional[int] = Field(description="Недели, в которые проводится занятие. 0 - четные, 1 - нечетные, 2 - все")
    day: str = Field(description="День недели")
    date_start: Optional[date] = Field(description="Дата начала занятия")
    date_end: Optional[date] = Field(description="Дата конца занятия")
    type: Optional[str] = Field(description="Тип занятия")
    name: str = Field(description="Название занятия")
    subgroup: Optional[str] = Field(description="Подгруппа, у которого проводится занятие")
    group: Optional[str] = Field(description="Группа, у которого проводится занятие")
    course: str = Field(description="Курс обученя")
    room: Optional[str] = Field(description="Аудитория в которой проводится занятие")
    academic: str = Field(description="Ученое звание")
    teacher: Optional[str] = Field(description="ФИО преподавателей")
    lang: str = Field(description="Язык (для перевода)")

    @field_validator("date_start", mode="before")
    def change_date_start(cls, value):
        if isinstance(value, str):
            if value == "":
                return None
            date_ = value.split('.')
            date_.reverse()
            return "-".join(date_)
        return None

    @field_validator("date_end", mode="before")
    def change_date_end(cls, value):
        if isinstance(value, str):
            if value == "":
                return None
            date_ = value.split('.')
            date_.reverse()
            return "-".join(date_)
        return None

    def __hash__(self):
        return hash(
            str(self.time_start.isoformat()) +
            str(self.time_end.isoformat()) +
            str(self.dot) +
            str(self.weeks) +
            str(self.date_start.isoformat()) +
            str(self.date_end.isoformat()) +
            str(self.type) +
            str(self.name) +
            str(self.subgroup) +
            str(self.course) +
            str(self.day)
        )

    def __eq__(self, other):
        return self.time_start == other.time_start and \
            self.time_end == other.time_end and \
            self.dot == other.dot and \
            self.weeks == other.weeks and \
            self.date_start == other.date_start and \
            self.date_end == other.date_end and \
            self.course == other.course and \
            self.day == other.day and \
            self.type == other.type and \
            self.name == other.name and \
            self.subgroup == other.subgroup


class LessonLoading(Base):
    time_start: time = Field(description="Время начала занятия")
    time_end: time = Field(description="Время конец занятия")
    dot: bool = Field(description="Динстанционное ли занятие")
    weeks: Optional[int] = Field(description="Недели, в которые проводится занятие. 0 - четные, 1 - нечетные, 2 - все")
    day: str = Field(description="День недели")
    date_start: Optional[date] = Field(description="Дата начала занятия")
    date_end: Optional[date] = Field(description="Дата конца занятия")
    type: Optional[str] = Field(description="Тип занятия")
    name: str = Field(description="Название занятия")
    subgroup: Optional[str] = Field(description="Подгруппа, у которой проводится занятие")
    groups: List[str] = Field(description="Группа, у которой проводится занятие")
    rooms: List[str] = Field(description="Аудитория в которой проводится занятие")
    teachers: List[str] = Field(description="Имена преподавателей")
    lang: str = Field(description="Язык (для перевода)")

    @field_validator("date_start", mode="before")
    def change_date_start(cls, value):
        if isinstance(value, str):
            if value == "":
                return None
            date_ = value.split('.')
            date_.reverse()
            return "-".join(date_)
        return None

    @field_validator("date_end", mode="before")
    def change_date_end(cls, value):
        if isinstance(value, str):
            if value == "":
                return None
            date_ = value.split('.')
            date_.reverse()
            return "-".join(date_)
        return None
    