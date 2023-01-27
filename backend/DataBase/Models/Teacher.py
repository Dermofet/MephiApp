import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.DataBase.connection import Base
from backend.DataBase.Models.AssociationTables import AT_lesson_teacher


class Teacher(Base):
    __tablename__ = "teachers"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    online_url = Column(String(200), nullable=True)
    alt_online_url = Column(String(200), nullable=True)

    trans = relationship("TeacherTranslate",
                         back_populates="teacher",
                         lazy="selectin",
                         uselist=True)
    lessons = relationship("Lesson", back_populates="teachers", lazy="selectin", uselist=True,
                           secondary=AT_lesson_teacher)
