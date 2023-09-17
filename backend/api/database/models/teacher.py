import uuid
from typing import Optional

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, WriteOnlyMapped

from backend.api.database.connection import Base
from backend.api.database.models.association_tables import AT_lesson_teacher


class TeacherModel(Base):
    __tablename__ = "teachers"

    guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    url: Mapped[Optional[str]]
    alt_url: Mapped[Optional[str]]

    lessons: WriteOnlyMapped["LessonModel"] = relationship(
        back_populates="teachers",
        secondary=AT_lesson_teacher,
        uselist=True,
    )
    trans: WriteOnlyMapped["TeacherTranslateModel"] = relationship(back_populates="teacher", uselist=True)

    def __repr__(self):
        return f"<Teacher {self.guid}>"
