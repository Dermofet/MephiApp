import copy
import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.connection import Base


class CorpsModel(Base):
    __tablename__ = "corps"
    __table_args__ = {'extend_existing': True}

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    name = Column(String(300), unique=True)
    rooms = relationship("RoomModel", back_populates="corps", primaryjoin="CorpsModel.guid == RoomModel.corps_guid",
                         uselist=True, lazy="joined")

    def __repr__(self):
        return f'\n\nguid: {self.guid}\n' \
               f'name: {self.name}\n' \
               f'rooms: {self.rooms}'

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == "rooms":
                # deepcopy the relationship by iterating over its elements
                setattr(result, k, [deepcopy(x, memo) for x in v])
            else:
                setattr(result, k, deepcopy(v, memo))
        return result
