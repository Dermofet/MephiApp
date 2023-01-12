import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.DataBase.connection import Base


class TeacherTranslate(Base):
    __tablename__ = "teacher_translate"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4(), primary_key=True, index=True, unique=True)
    name = Column(String(50), unique=True)
    fullname = Column(String(100), unique=True)
    lang_guid = Column(UUID(as_uuid=True), ForeignKey("languages.guid"))

    _teacher_ = relationship("Teacher",
                             back_populates="_teacher_translate_",
                             primaryjoin='TeacherTranslate.guid == Teacher.teacher_translate_guid')
    _lang_ = relationship("Language", back_populates="_teacher_translate_")
