import uuid

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.DataBase.connection import Base
from backend.DataBase.Models.AssociationTables import AT_lesson_group


class Group(Base):
    __tablename__ = "groups"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4(), primary_key=True, index=True, unique=True)
    name = Column(String(10), unique=True)
    course = Column(Integer)
    academic_guid = Column(UUID(as_uuid=True), ForeignKey("academics.guid"))

    academic = relationship("Academic", back_populates="groups", lazy="joined")
    lessons = relationship("Lesson", back_populates="groups", lazy="selectin", uselist=True, secondary=AT_lesson_group)
