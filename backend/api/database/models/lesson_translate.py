import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.api.database.connection import Base


class LessonTranslateModel(Base):
    __tablename__ = "lesson_translate"

    guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    type: Mapped[Optional[str]] = mapped_column(String(50))
    name: Mapped[str]
    subgroup: Mapped[Optional[str]] = mapped_column(String(200))
    lang: Mapped[str] = mapped_column(String(2))
    lesson_guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("lessons.guid"))

    lesson: Mapped["LessonModel"] = relationship("LessonModel", back_populates="trans", lazy="joined")
