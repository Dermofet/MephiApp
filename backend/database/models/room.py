import uuid

from app.backend.database.connection import Base
from app.backend.database.models.association_tables import AT_lesson_room
from app.backend.database.models.corps import CorpsModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class RoomModel(Base):
    __tablename__ = "rooms"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    number = Column(String(150), nullable=False)
    corps_guid = Column(UUID(as_uuid=True), ForeignKey("corps.guid"))

    corps = relationship("CorpsModel", back_populates="rooms", lazy="joined", uselist=False)
    lessons = relationship("LessonModel", back_populates="rooms", lazy="joined", uselist=True, secondary=AT_lesson_room)

    def __repr__(self):
        return f'<RoomModel:\n' \
               f' guid: {self.guid}\n' \
               f' number: {self.number}>'
