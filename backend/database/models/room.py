import uuid

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.connection import Base
from backend.database.models.association_tables import AT_lesson_room
from backend.database.models.corps import CorpsModel


class RoomModel(Base):
    __tablename__ = "rooms"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    number = Column(String(150), nullable=False)
    corps_guid = Column(UUID(as_uuid=True), ForeignKey("corps.guid"))

    lessons = relationship("LessonModel", back_populates="rooms", lazy="selectin", uselist=True,
                           secondary=AT_lesson_room)
    corps = relationship("CorpsModel", back_populates="rooms", lazy="joined", uselist=False)
