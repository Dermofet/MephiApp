import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.DataBase.connection import Base


class Teacher(Base):
    __tablename__ = "teachers"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    online_url = Column(String(200), nullable=True)
    alt_online_url = Column(String(200), nullable=True)
    teacher_translate_guid = Column(UUID(as_uuid=True), ForeignKey("teacher_translate.guid"))

    _teacher_translate_ = relationship("TeacherTranslate", back_populates="_teacher_")
    _lessons_ = relationship("Lesson", back_populates="_teacher_", primaryjoin="Teacher.guid == Lesson.teacher_guid")
