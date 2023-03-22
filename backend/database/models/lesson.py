import copy
import uuid

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.connection import Base
from backend.database.models.association_tables import *


class LessonModel(Base):
    __tablename__ = "lessons"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    time_start = Column(Time)
    time_end = Column(Time)
    dot = Column(Boolean, default=False)
    weeks = Column(Integer)
    date_start = Column(Date, nullable=True)
    date_end = Column(Date, nullable=True)
    day = Column(String(50))

    trans = relationship("LessonTranslateModel", back_populates="lesson", lazy="joined", uselist=True,
                         primaryjoin="LessonModel.guid == LessonTranslateModel.lesson_guid")
    groups = relationship("GroupModel", back_populates="lessons", lazy="joined", uselist=True,
                          secondary=AT_lesson_group)
    teachers = relationship("TeacherModel", back_populates="lessons", lazy="joined", uselist=True,
                            secondary=AT_lesson_teacher)
    rooms = relationship("RoomModel", back_populates="lessons", lazy="joined", uselist=True, secondary=AT_lesson_room)

    def __repr__(self):
        return f'<LessonModel:\n' \
               f' guid: {self.guid}\n' \
               f' time_start: {self.time_start}\n' \
               f' time_end: {self.time_end}\n' \
               f' dot: {self.dot}\n' \
               f' weeks: {self.weeks}\n' \
               f' date_start: {self.date_start}\n' \
               f' date_end: {self.date_end}\n' \
               f' day: {self.day}\n' \
               f' trans: {self.trans}\n' \
               f' groups: {self.groups}\n' \
               f' teachers: {self.teachers}\n' \
               f' rooms: {self.rooms}>'

    def __eq__(self, other):
        if type(other) is type(self):
            self_rooms = set(self.rooms)
            other_rooms = set(other.rooms)
            return (self.time_start == other.time_start and
                    self.time_end == other.time_end and
                    self.dot == other.dot and
                    self.weeks == other.weeks and
                    self.date_start == other.date_start and
                    self.date_end == other.date_end and
                    self.day == other.day and
                    self_rooms == other_rooms and
                    self.trans[0].name == other.trans[0].name and
                    self.trans[0].subgroup == other.trans[0].subgroup and
                    self.trans[0].type == other.trans[0].type and
                    self.trans[0].lang == other.trans[0].lang)

    def __hash__(self):
        self_rooms = [str(room.number) for room in self.rooms]
        self_trans = [str(tr.name) + str(tr.subgroup) + str(tr.lang) + str(tr.type) for tr in self.trans]
        return hash(str(self.time_start) + str(self.time_end) + str(self.dot) + str(self.weeks) + str(self.date_start)
                    + str(self.date_end) + str(self.day) + "".join(self_rooms) + "".join(self_trans))
