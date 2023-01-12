import uuid

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.DataBase.connection import Base


class Lesson(Base):
    __tablename__ = "lessons"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    time_start = Column(String(50))
    time_end = Column(String(50))
    dot = Column(Boolean, default=False)
    weeks = Column(Integer)
    date_start = Column(String(15))
    date_end = Column(String(15))
    day = Column(String(15))

    room_guid = Column(UUID(as_uuid=True), ForeignKey("rooms.guid"))
    group_guid = Column(UUID(as_uuid=True), ForeignKey("groups.guid"))
    teacher_guid = Column(UUID(as_uuid=True), ForeignKey("teachers.guid"))
    lesson_translate_guid = Column(UUID(as_uuid=True), ForeignKey("lesson_translate.guid"))

    _group_ = relationship("Group", back_populates="_lessons_")
    _teacher_ = relationship("Teacher", back_populates="_lessons_")
    _room_ = relationship("Room", back_populates="_lessons_")
    _lesson_translate_ = relationship("LessonTranslate", back_populates="_lessons_")
