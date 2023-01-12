import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.DataBase.connection import Base


class Corps(Base):
    __tablename__ = "corps"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4(), primary_key=True, index=True, unique=True)
    name = Column(String(300), unique=True)
    _rooms_ = relationship("Room", back_populates="_corps_")
