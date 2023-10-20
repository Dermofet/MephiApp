import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, WriteOnlyMapped, mapped_column, relationship

from backend.api.database.connection import Base
from backend.api.database.models.association_tables import AT_lesson_group


class GroupModel(Base):
    __tablename__ = "groups"

    guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    name: Mapped[str] = mapped_column(String(10), unique=True)
    course: Mapped[int]
    academic_guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("academics.guid"))

    academic: Mapped["AcademicModel"] = relationship(back_populates="groups")
    lessons: WriteOnlyMapped["LessonModel"] = relationship(
        back_populates="groups", secondary=AT_lesson_group, uselist=True
    )
