import uuid

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.DataBase.connection import Base
from backend.DataBase.Models.AssociationTables import AT_lesson_room
from backend.DataBase.Models.Corps import Corps


class Room(Base):
    __tablename__ = "rooms"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4(), primary_key=True, index=True, unique=True)
    number = Column(String(15), nullable=False)
    corps_guid = Column(UUID(as_uuid=True), ForeignKey("corps.guid"))

    lessons = relationship("Lesson", back_populates="rooms", lazy="selectin", uselist=True, secondary=AT_lesson_room)
    corps = relationship("Corps", back_populates="rooms", lazy="joined", uselist=False)
