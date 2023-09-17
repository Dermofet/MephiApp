import datetime
from copy import deepcopy
from datetime import date, time
from typing import Optional

from pydantic import field_validator, ConfigDict, UUID4, BaseModel, Field, ValidationError

from backend.api.database.models.lesson import LessonModel
from backend.api.database.models.lesson_translate import LessonTranslateModel
from backend.api.schemas.group import GroupOutputSchema, GroupSchema
from backend.api.schemas.lesson_translate import LessonTranslateOutputSchema, LessonTranslateSchema
from backend.api.schemas.room import RoomOutputSchema, RoomSchema
from backend.api.schemas.teacher import TeacherOutputSchema, TeacherSchema


class LessonBaseSchema(BaseModel):
    time_start: time = Field(description="Время начала занятия")
    time_end: time = Field(description="Время конец занятия")
    dot: bool = Field(description="Динстанционное ли занятие")
    weeks: int = Field(description="Недели, в которые проводится занятие. 0 - четные, 1 - нечетные, 2 - все")
    day: str = Field(description="День недели")
    date_start: Optional[date] = Field(description="Дата начала занятия")
    date_end: Optional[date] = Field(description="Дата конца занятия")

    @field_validator("date_start", mode="before")
    def change_date_start(cls, value):
        if isinstance(value, str):
            date_ = value.split('.')
            date_.reverse()
            return "-".join(date_)
        return None

    @field_validator("date_end", mode="before")
    def change_date_end(cls, value):
        if isinstance(value, str):
            date_ = value.split('.')
            date_.reverse()
            return "-".join(date_)
        return None


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

    @field_validator("teacher_name", mode="before")
    def none_teacher(cls, value):
        if isinstance(value, type(None)):
            return "None"
        elif isinstance(value, str):
            return value
        else:
            raise ValidationError('Имя преподавателя не строка')


class LessonOutputSchema(LessonBaseSchema):
    time_start: str = Field(description="Время начала занятия")
    time_end: str = Field(description="Время конца занятия")
    date_start: Optional[str] = Field(description="Дата начала занятия")
    date_end: Optional[str] = Field(description="Дата начала занятия")
    weeks: list[int] = Field(description="Недели, в которые проводится занятие")
    trans: LessonTranslateOutputSchema = Field(description="Список полей, нуждающихся в переводе, на разных "
                                                           "языках")
    groups: list[GroupOutputSchema] = Field(description="Список групп, которые находятся на занятии")
    teachers: list[TeacherOutputSchema] = Field(description="Список преподавателей, которые находятся на занятии")
    rooms: list[RoomOutputSchema] = Field(description="Список аудиторий, в которой проводится занятие")

    @field_validator("weeks", mode="before")
    def change_weeks(cls, value):
        if isinstance(value, int):
            if value == 0:
                return list(range(2, 16, 2))
            elif value == 1:
                return list(range(1, 15, 2))
            elif value == 2:
                return list(range(1, 16))
        elif isinstance(value, list):
            return value
        else:
            raise ValueError('Неверное значение для weeks. Оно может быть 0 - четные недели, 1 - нечетные недели, '
                             '2 - все недели.')


class LessonSchema(LessonBaseSchema):
    guid: Optional[UUID4] = Field(description="ID")
    time_start: str = Field(description="Время начала занятия")
    time_end: str = Field(description="Время конца занятия")
    date_start: Optional[str] = Field(description="Дата начала занятия")
    date_end: Optional[str] = Field(description="Дата начала занятия")
    trans: LessonTranslateSchema = Field(description="Список полей, нуждающихся в переводе, на разных языках")
    groups: list[GroupSchema] = Field(description="Список групп, которые находятся на занятии")
    teachers: list[TeacherSchema] = Field(description="Список преподавателей, которые находятся на занятии")
    rooms: list[RoomSchema] = Field(description="Список аудиторий, в которой проводится занятие")

    def clone(self):
        return LessonSchema(
            guid=self.guid,
            time_start=self.time_start,
            time_end=self.time_end,
            date_start=self.date_start,
            date_end=self.date_end,
            dot=self.dot,
            weeks=self.weeks,
            day=self.day,
            trans=[self.trans.clone()],
            groups=[group.clone() for group in self.groups],
            teachers=[teacher.clone() for teacher in self.teachers],
            rooms=[room.clone() for room in self.rooms]
        )

    def to_model(self):
        date_start = self.date_start.split('.') \
                if self.date_start is not None else None

        if date_start is not None:
            date_start.reverse()
            date_start = datetime.datetime.strptime("-".join(date_start),
                                                    '%Y-%m-%d').date()

        date_end = self.date_start.split('.') \
            if self.date_start is not None else None

        if date_end is not None:
            date_end.reverse()
            date_end = datetime.datetime.strptime("-".join(date_end), '%Y-%m-%d').date()

        return LessonModel(
            guid=self.guid,
            time_start=datetime.datetime.strptime(self.time_start, "%H:%M").time(),
            time_end=datetime.datetime.strptime(self.time_end, "%H:%M").time(),
            date_start=date_start,
            date_end=date_end,
            dot=self.dot,
            weeks=self.weeks,
            day=self.day,
            trans=[self.trans.to_model()],
            groups=[group.to_model() for group in self.groups],
            teachers=[teacher.to_model() for teacher in self.teachers],
            rooms=[room.to_model() for room in self.rooms]
        )

    def __eq__(self, other):
        if isinstance(other, LessonSchema):
            self_rooms = {room.number for room in self.rooms}
            other_rooms = {room.number for room in other.rooms}
            self_trans = set(self.trans)
            other_trans = set(other.trans)
            return (self.time_start == other.time_start and
                    self.time_end == other.time_end and
                    self.dot == other.dot and
                    self.weeks == other.weeks and
                    self.date_start == other.date_start and
                    self.date_end == other.date_end and
                    self.day == other.day and
                    self_rooms == other_rooms and
                    self_trans == other_trans)
        return False

    def __hash__(self):
        self_rooms = [str(room.number) for room in self.rooms]
        self_trans = str(self.trans.name) + str(self.trans.subgroup) + str(self.trans.lang) + str(self.trans.type)
        return hash(str(self.time_start) + str(self.time_end) + str(self.dot) + str(self.weeks) + str(self.date_start)
                    + str(self.date_end) + str(self.day) + "".join(self_rooms) + self_trans)

    @field_validator("trans", mode="before")
    def check_trans(cls, trans):
        if not isinstance(trans, list):
            raise ValueError(f"trans - {type(trans)}, должен быть list")
        for tr in trans:
            if isinstance(tr, (LessonTranslateModel, LessonTranslateSchema)):
                return tr
            else:
                raise ValueError(f"trans содержит {type(tr)}, "
                                 f"должен быть LessonTranslateModel или LessonTranslateSchema.")

    @field_validator("time_start", mode="before")
    def change_time_start(cls, value):
        if isinstance(value, time):
            return value.strftime('%H:%M')
        elif isinstance(value, int):
            print(f'Int value: {value}, type: {type(value)}')
        elif isinstance(value, str):
            return value
        else:
            ValueError(f"time_start - неверный тип данных. Ожидалось time, было получено {type(value)}")

    @field_validator("time_end", mode="before")
    def change_time_end(cls, value):
        if isinstance(value, time):
            return value.strftime('%H:%M')
        elif isinstance(value, int):
            print(f'Int value: {value}, type: {type(value)}')
        elif isinstance(value, str):
            return value
        else:
            ValueError(f"time_end - неверный тип данных. Ожидалось time, было получено {type(value)}")

    @field_validator("date_start", mode="before")
    def change_date_start(cls, value):
        if isinstance(value, date):
            return value.strftime('%m.%d.%Y')
        elif isinstance(value, str):
            return value
        elif isinstance(value, type(None)):
            return None
        else:
            ValueError(f"date_start - неверный тип данных. Ожидалось date, было получено {type(value)}")

    @field_validator("date_end", mode="before")    
    def change_date_end(cls, value):
        if isinstance(value, date):
            return value.strftime('%m.%d.%Y')
        elif isinstance(value, str):
            return value
        elif isinstance(value, type(None)):
            return None
        else:
            ValueError(f"date_end - неверный тип данных. Ожидалось date, было получено {type(value)}")
    model_config = ConfigDict(from_attributes=True)


class LessonsByBaseSchema(BaseModel):
    lessons: list[LessonOutputSchema] = Field(description="Занятия определенной группы")
    lang: str = Field(description="Язык")


associative_dict = {
    "Понедельник": "1",
    "Вторник": "2",
    "Среда": "3",
    "Четверг": "4",
    "Пятница": "5",
    "Суббота": "6",
    "Воскресенье": "7"
}


class LessonsByGroupSchema(LessonsByBaseSchema):
    group: str = Field(description="Поля группы")

    def dict(self, *args, **kwargs):
        res = {
            "group": self.group,
            "schedule": {
                "1": [],
                "2": [],
                "3": [],
                "4": [],
                "5": [],
                "6": [],
                "7": []
            }
        }

        self.lessons = sorted(self.lessons, key=lambda lesson: (lesson.day, lesson.time_start))

        for lesson in self.lessons:
            _lesson_ = {
                "time_start": lesson.time_start,
                "time_end": lesson.time_end,
                "lesson_group": []
            }
            _teachers_ = [{
                "teacher_name": teacher.name,
                "teacher_fullname": teacher.fullname
            } for teacher in lesson.teachers]
            _rooms_ = {room.number for room in lesson.rooms}
            _groups_ = {group.name for group in lesson.groups}
            day = associative_dict[lesson.day]

            _lesson_group_ = {
                "name": lesson.trans.name,
                "subgroup": lesson.trans.subgroup,
                "type": lesson.trans.type,
                "dot": lesson.dot,
                "weeks": lesson.weeks,
                "date_start": lesson.date_start,
                "date_end": lesson.date_end,
                "teachers": _teachers_,
                "rooms": _rooms_,
                "groups": _groups_,
            }
            flag = False
            for i in range(len(res["schedule"][day])):
                if lesson.time_start == res["schedule"][day][i]["time_start"]:
                    res["schedule"][day][i]["lesson_group"].append(deepcopy(_lesson_group_))
                    flag = True
                    break

            if not flag:
                _lesson_["lesson_group"].append(deepcopy(_lesson_group_))
                res["schedule"][day].append(deepcopy(_lesson_))
        return res


class LessonsByTeacherSchema(LessonsByBaseSchema):
    name: str = Field(description="Имя")
    fullname: Optional[str] = Field(description="Фамилия")
    url: Optional[str] = Field(description="Ссылка на дискорд")
    alt_url: Optional[str] = Field(description="Ссылка на дискорд")
    
    def dict(self, *args, **kwargs):
        res = {
            "name": self.name,
            "fullname": self.fullname,
            "url": self.url,
            "alt_url": self.alt_url,
            "schedule": {
                "1": [],
                "2": [],
                "3": [],
                "4": [],
                "5": [],
                "6": [],
                "7": []
            }
        }

        self.lessons = sorted(self.lessons, key=lambda lesson: (lesson.day, lesson.time_start))

        for lesson in self.lessons:
            _lesson_ = {
                "time_start": lesson.time_start,
                "time_end": lesson.time_end,
                "lesson_group": []
            }
            _teachers_ = [{
                "teacher_name": teacher.name,
                "teacher_fullname": teacher.fullname,
                "url": teacher.url,
                "alt_url": teacher.alt_url
            } for teacher in lesson.teachers]
            _rooms_ = {room.number for room in lesson.rooms}
            _groups_ = {group.name for group in lesson.groups}
            _lesson_group_ = {
                "name": lesson.trans.name,
                "subgroup": lesson.trans.subgroup,
                "type": lesson.trans.type,
                "dot": lesson.dot,
                "weeks": lesson.weeks,
                "date_start": lesson.date_start,
                "date_end": lesson.date_end,
                "groups": _groups_,
                "rooms": _rooms_,
                "teachers": _teachers_
            }

            day = associative_dict[lesson.day]

            flag = False
            for i in range(len(res["schedule"][day])):
                if lesson.time_start == res["schedule"][day][i]["time_start"]:
                    res["schedule"][day][i]["lesson_group"].append(deepcopy(_lesson_group_))
                    flag = True
                    break

            if not flag:
                _lesson_["lesson_group"].append(deepcopy(_lesson_group_))
                res["schedule"][day].append(deepcopy(_lesson_))

        return res
