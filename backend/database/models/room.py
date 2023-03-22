import copy
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

    corps = relationship("CorpsModel", back_populates="rooms", lazy="joined", uselist=False)
    lessons = relationship("LessonModel", back_populates="rooms", lazy="joined", uselist=True, secondary=AT_lesson_room)

    def __repr__(self):
        return f'<RoomModel: {self.number}>'

    def __eq__(self, other):
        if isinstance(other, RoomModel):
            return self.number == other.number
        return False

    def __hash__(self):
        return hash(self.number)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result
