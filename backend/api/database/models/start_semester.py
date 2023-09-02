import uuid

from sqlalchemy import Column, Date, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.connection import Base


class StartSemesterModel(Base):
    __tablename__ = "start_semester"
    __table_args__ = {'extend_existing': True}

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    date = Column(Date)
