import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.connection import Base
from backend.database.models.association_tables import *


class LessonModel(Base):
    __tablename__ = "lessons"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    time_start = Column(String(50))
    time_end = Column(String(50))
    dot = Column(Boolean, default=False)
    weeks = Column(Integer)
    date_start = Column(String(15), nullable=True)
    date_end = Column(String(15), nullable=True)
    day = Column(String(50))

    groups = relationship("GroupModel", back_populates="lessons", lazy="selectin", uselist=True, secondary=AT_lesson_group)
    teachers = relationship("TeacherModel", back_populates="lessons", lazy="selectin", uselist=True, secondary=AT_lesson_teacher)
    rooms = relationship("RoomModel", back_populates="lessons", lazy="selectin", uselist=True, secondary=AT_lesson_room)
    trans = relationship("LessonTranslateModel", back_populates="lesson", lazy="selectin", uselist=True)
