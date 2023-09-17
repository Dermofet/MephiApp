import datetime
import uuid
from typing import Optional

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, WriteOnlyMapped

from backend.api.database.connection import Base
from backend.api.database.models.association_tables import AT_lesson_group, AT_lesson_room, AT_lesson_teacher


class LessonModel(Base):
    __tablename__ = "lessons"

    guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    time_start: Mapped[datetime.time]
    time_end: Mapped[datetime.time]
    dot: Mapped[bool] = mapped_column(default=False)
    weeks: Mapped[int]
    date_start: Mapped[Optional[datetime.date]]
    date_end: Mapped[Optional[datetime.date]]
    day: Mapped[str] = mapped_column(String(50))

    trans: WriteOnlyMapped["LessonTranslateModel"] = relationship(
        back_populates="lesson",
        uselist=True,
    )
    groups: WriteOnlyMapped["GroupModel"] = relationship(
        back_populates="lessons",
        secondary=AT_lesson_group,
        uselist=True,
    )
    teachers: WriteOnlyMapped["TeacherModel"] = relationship(
        back_populates="lessons",
        secondary=AT_lesson_teacher,
        uselist=True,
    )
    rooms: WriteOnlyMapped["RoomModel"] = relationship(
        back_populates="lessons",
        secondary=AT_lesson_room,
        uselist=True,
    )
