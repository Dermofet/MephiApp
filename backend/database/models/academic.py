import uuid

from app.backend.database.connection import Base
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class AcademicModel(Base):
    __tablename__ = "academics"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    name = Column(String(100), unique=True)

    groups = relationship("GroupModel", back_populates="academic",
                          primaryjoin='AcademicModel.guid == GroupModel.academic_guid')
