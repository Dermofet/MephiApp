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

    # group_guid = Column(UUID(as_uuid=True), ForeignKey("groups.guid"), nullable=True)
    # teacher_guid = Column(UUID(as_uuid=True), ForeignKey("teachers.guid"), nullable=True)
    # room_guid = Column(UUID(as_uuid=True), ForeignKey("rooms.guid"), nullable=True)
    #
    # group = relationship("GroupModel", back_populates="lessons", lazy="joined")
    # teacher = relationship("TeacherModel", back_populates="lessons", lazy="joined")
    # room = relationship("RoomModel", back_populates="lessons", lazy="joined")

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
