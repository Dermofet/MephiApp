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
    subgroup = Column(String(100), nullable=True)
    lang = Column(String(2))
    lesson_guid = Column(UUID(as_uuid=True), ForeignKey("lessons.guid"))

    lesson = relationship("Lesson", back_populates="trans", lazy="joined", uselist=False)
