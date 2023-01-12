import uuid

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.DataBase.connection import Base


class Group(Base):
    __tablename__ = "groups"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4(), primary_key=True, index=True, unique=True)
    name = Column(String(10), unique=True)
    course = Column(Integer)
    academic_guid = Column(UUID(as_uuid=True), ForeignKey("academics.guid"))

    _academic_ = relationship("Academic", back_populates="_groups_")
    _lessons_ = relationship("Lesson", back_populates="_group_", primaryjoin='Group.guid == Lesson.group_guid')
