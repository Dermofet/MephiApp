import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.DataBase.connection import Base


class Academic(Base):
    __tablename__ = "academics"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4(), primary_key=True, index=True, unique=True)
    name = Column(String(100), unique=True)

    _groups_ = relationship("Group", back_populates="_academic_", primaryjoin='Academic.guid == Group.academic_guid')
