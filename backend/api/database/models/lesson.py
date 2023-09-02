import datetime
import uuid
from typing import List, Optional

from sqlalchemy import Boolean, Date, Integer, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    trans: Mapped[List["LessonTranslateModel"]] = relationship(
        "LessonTranslateModel",
        back_populates="lesson",
        lazy="joined",
    )
    groups: Mapped[List["GroupModel"]] = relationship(
        "GroupModel",
        back_populates="lessons",
        lazy="joined",
        secondary=AT_lesson_group,
    )
    teachers: Mapped[List["TeacherModel"]] = relationship(
        "TeacherModel",
        back_populates="lessons",
        lazy="joined",
        secondary=AT_lesson_teacher,
    )
    rooms: Mapped[List["RoomModel"]] = relationship(
        "RoomModel",
        back_populates="lessons",
        lazy="joined",
        secondary=AT_lesson_room,
    )

