import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.connection import Base


class AcademicModel(Base):
    __tablename__ = "academics"
    __table_args__ = {'extend_existing': True}

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    name = Column(String(100), unique=True)

    groups = relationship("GroupModel", back_populates="academic",
                          primaryjoin='AcademicModel.guid == GroupModel.academic_guid')
