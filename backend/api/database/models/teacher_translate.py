import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.api.database.connection import Base


class TeacherTranslateModel(Base):
    __tablename__ = "teacher_translate"

    guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    name: Mapped[str]
    fullname: Mapped[Optional[str]]
    lang: Mapped[str] = mapped_column(String(2))
    teacher_guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("teachers.guid"))

    teacher: Mapped["TeacherModel"] = relationship(
        back_populates="trans",
        uselist=False,
    )

    def __repr__(self) -> str:
        return f"<TeacherTranslateModel {self.name, self.lang}>"