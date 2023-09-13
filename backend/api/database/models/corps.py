import uuid
from typing import List

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship, WriteOnlyMapped

from backend.api.database.connection import Base


class CorpsModel(Base):
    __tablename__ = "corps"

    guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    name: Mapped[str] = mapped_column(String(300), unique=True)
    rooms: WriteOnlyMapped["RoomModel"] = relationship(back_populates="corps", uselist=True)
