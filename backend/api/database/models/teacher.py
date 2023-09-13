import uuid
from typing import List, Optional
from sqlalchemy import String

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, WriteOnlyMapped

from backend.api.database.connection import Base
from backend.api.database.models.association_tables import AT_lesson_teacher


class TeacherModel(Base):
    __tablename__ = "teachers"

    guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    name: Mapped[str]
    fullname: Mapped[Optional[str]]
    lang: Mapped[str] = mapped_column(String(2))

    lessons: WriteOnlyMapped["LessonModel"] = relationship(
        back_populates="teachers",
        secondary=AT_lesson_teacher,
        uselist=True,
    )
