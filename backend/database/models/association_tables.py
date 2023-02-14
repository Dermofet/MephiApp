from sqlalchemy import Column, ForeignKey, String, insert
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table

from backend.database.connection import Base

AT_lesson_group = Table(
    "AT_lesson_group",
    Base.metadata,
    Column("lesson_guid", ForeignKey("lessons.guid"), primary_key=True),
    Column("group_guid", ForeignKey("groups.guid"), primary_key=True)
)

AT_lesson_teacher = Table(
    "AT_lesson_teacher",
    Base.metadata,
    Column("lesson_guid", ForeignKey("lessons.guid"), primary_key=True),
    Column("teacher_guid", ForeignKey("teachers.guid"), primary_key=True)
)

AT_lesson_room = Table(
    "AT_lesson_room",
    Base.metadata,
    Column("lesson_guid", ForeignKey("lessons.guid"), primary_key=True),
    Column("room_guid", ForeignKey("rooms.guid"), primary_key=True)
)


# class LessonGroup(Base):
#     __tablename__ = 'AT_lesson_group'
#
#     lesson_guid = Column(UUID(as_uuid=True), ForeignKey("lessons.guid"), primary_key=True)
#     group_guid = Column(UUID(as_uuid=True), ForeignKey("groups.guid"), primary_key=True)
#
#     _lessons_ = relationship("Lesson", back_populates="_groups_")
#     _groups_ = relationship("Group", back_populates="_lessons_")
#
#
# class LessonTeacher(Base):
#     __tablename__ = 'AT_lesson_teacher'
#
#     lesson_guid = Column(UUID(as_uuid=True), ForeignKey("lessons.guid"), primary_key=True)
#     teacher_guid = Column(UUID(as_uuid=True), ForeignKey("teachers.guid"), primary_key=True)
#
#     _lessons_ = relationship("Lesson", back_populates="_teachers_")
#     _teachers_ = relationship("Teacher", back_populates="_lessons_")
#
#
# class LessonRoom(Base):
#     __tablename__ = 'AT_lesson_room'
#
#     lesson_guid = Column(UUID(as_uuid=True), ForeignKey("lessons.guid"), primary_key=True)
#     room_guid = Column(UUID(as_uuid=True), ForeignKey("rooms.guid"), primary_key=True)
#
#     _lessons_ = relationship("Lesson", back_populates="_rooms_")
#     _rooms_ = relationship("Room", back_populates="_lessons_")
