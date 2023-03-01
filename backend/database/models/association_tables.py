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
