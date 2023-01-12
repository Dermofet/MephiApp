import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.DataBase.connection import Base


class LessonTranslate(Base):
    __tablename__ = "lesson_translate"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4(), primary_key=True, index=True, unique=True)
    type = Column(String(10))
    name = Column(String(200))
    subgroup = Column(String(100))
    lang_guid = Column(UUID(as_uuid=True), ForeignKey("languages.guid"))

    _lang_ = relationship("Language", back_populates="_lesson_translate_")
    _lessons_ = relationship("Lesson",
                             back_populates="_lesson_translate_",
                             primaryjoin='LessonTranslate.guid == Lesson.lesson_translate_guid')
