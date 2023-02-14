import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.connection import Base


class CorpsModel(Base):
    __tablename__ = "corps"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    name = Column(String(300), unique=True)
    rooms = relationship("RoomModel", back_populates="corps", primaryjoin="CorpsModel.guid == RoomModel.corps_guid",
                         uselist=True, lazy="selectin")
