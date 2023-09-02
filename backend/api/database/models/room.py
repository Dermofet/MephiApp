import uuid
from typing import List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.api.database.connection import Base
from backend.api.database.models.association_tables import AT_lesson_room


class RoomModel(Base):
    __tablename__ = "rooms"

    guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    number: Mapped[str] = mapped_column(String(150), unique=True)
    corps_guid: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("corps.guid"))

    corps: Mapped["CorpsModel"] = relationship("CorpsModel", back_populates="rooms", lazy="joined")
    lessons: Mapped[List["LessonModel"]] = relationship(
        "LessonModel",
        back_populates="rooms",
        lazy="joined",
        secondary=AT_lesson_room,
    )

    def __repr__(self):
        return f"| {self.number}, {self.corps.guid if self.corps else None} |"