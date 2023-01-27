import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.DataBase.connection import Base
from backend.DataBase.Models.AssociationTables import *


class Lesson(Base):
    __tablename__ = "lessons"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    time_start = Column(String(50))
    time_end = Column(String(50))
    dot = Column(Boolean, default=False)
    weeks = Column(Integer)
    date_start = Column(String(15), nullable=True)
    date_end = Column(String(15), nullable=True)
    day = Column(String(15))

    groups = relationship("Group", back_populates="lessons", lazy="selectin", uselist=True, secondary=AT_lesson_group)
    teachers = relationship("Teacher", back_populates="lessons", lazy="selectin", uselist=True, secondary=AT_lesson_teacher)
    rooms = relationship("Room", back_populates="lessons", lazy="selectin", uselist=True, secondary=AT_lesson_room)
    trans = relationship("LessonTranslate", back_populates="lesson", lazy="selectin", uselist=True,
                         primaryjoin="LessonTranslate.lesson_guid == Lesson.guid")

    # def __repr__(self):
    #     return f'guid = {self.guid}\n' \
    #            f'time_start = {self.time_start}\n' \
    #            f'time_end = {self.time_end}\n' \
    #            f'dot = {self.dot}\n' \
    #            f'weeks = {self.weeks}\n' \
    #            f'date_start = {self.date_start}\n' \
    #            f'date_end = {self.date_end}\n' \
    #            f'day = {self.day}\n'
