from sqlalchemy import Column, ForeignKey
from sqlalchemy.schema import Table

from backend.api.database.connection import Base

AT_lesson_group = Table(
    "AT_lesson_group",
    Base.metadata,
    Column("lesson_guid", ForeignKey("lessons.guid"), primary_key=True),
    Column("group_guid", ForeignKey("groups.guid"), primary_key=True),
    extend_existing=True
)

AT_lesson_teacher = Table(
    "AT_lesson_teacher",
    Base.metadata,
    Column("lesson_guid", ForeignKey("lessons.guid"), primary_key=True),
    Column("teacher_guid", ForeignKey("teachers.guid"), primary_key=True),
    extend_existing=True
)

AT_lesson_room = Table(
    "AT_lesson_room",
    Base.metadata,
    Column("lesson_guid", ForeignKey("lessons.guid"), primary_key=True),
    Column("room_guid", ForeignKey("rooms.guid"), primary_key=True),
    extend_existing=True
)
