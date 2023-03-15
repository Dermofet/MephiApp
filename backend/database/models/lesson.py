import uuid

from app.backend.database.connection import Base
from app.backend.database.models.association_tables import *
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


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
               f' group: {self.group}\n' \
               f' teacher: {self.teacher}\n' \
               f' room: {self.room}>'

    def __eq__(self, other):
        if isinstance(other, LessonModel):
            self_rooms = set(room.number for room in self.rooms)
            other_rooms = set(room.number for room in other.rooms)
            return self.time_start == other.time_start and self.time_end == other.time_end and self.dot == other.dot and \
                self.weeks == other.weeks and self.date_start == other.date_start and self.date_end == other.date_end and \
                self.day == other.day and self_rooms == other_rooms
        return False

    def __hash__(self):
        self_rooms = set(room.number for room in self.rooms)
        return hash((self.time_start, self.time_end, self.dot, self.weeks, self.date_start, self.date_end, self.day,
                     self_rooms))
