import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.DataBase.connection import Base


class Language(Base):
    __tablename__ = "languages"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    lang = Column(String(2), unique=True)

    _lesson_translate_ = relationship("LessonTranslate",
                                      back_populates="_lang_",
                                      primaryjoin='Language.guid == LessonTranslate.lang_guid')
    _teacher_translate_ = relationship("TeacherTranslate",
                                       back_populates="_lang_",
                                       primaryjoin='Language.guid == TeacherTranslate.lang_guid')
