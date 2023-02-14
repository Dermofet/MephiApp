import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.connection import Base
from backend.database.models.association_tables import AT_lesson_teacher


class TeacherModel(Base):
    __tablename__ = "teachers"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    online_url = Column(String, nullable=True, unique=True)
    alt_online_url = Column(String, nullable=True, unique=True)

    trans = relationship("TeacherTranslateModel", back_populates="teacher", lazy="selectin", uselist=True)
    lessons = relationship("LessonModel", back_populates="teachers", lazy="selectin", uselist=True,
                           secondary=AT_lesson_teacher)
