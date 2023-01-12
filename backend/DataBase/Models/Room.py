import uuid

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.DataBase.connection import Base
from backend.DataBase.Models.Corps import Corps


class Room(Base):
    __tablename__ = "rooms"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4(), primary_key=True, index=True, unique=True)
    number = Column(String(15), nullable=False)
    corps_guid = Column(UUID(as_uuid=True), ForeignKey("corps.guid"))

    _lessons_ = relationship("Lesson", back_populates="_room_", primaryjoin="Room.guid == Lesson.room_guid")
    _corps_ = relationship("Corps", back_populates="_rooms_")
