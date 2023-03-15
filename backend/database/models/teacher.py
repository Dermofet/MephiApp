import uuid

from app.backend.database.connection import Base
from app.backend.database.models.association_tables import AT_lesson_teacher
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class TeacherModel(Base):
    __tablename__ = "teachers"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    online_url = Column(String, nullable=True, unique=True)
    alt_online_url = Column(String, nullable=True, unique=True)

    trans = relationship("TeacherTranslateModel", back_populates="teacher", lazy="joined", uselist=True,
                         primaryjoin="TeacherModel.guid == TeacherTranslateModel.teacher_guid")
    lessons = relationship("LessonModel", back_populates="teachers", lazy="joined", uselist=True,
                           secondary=AT_lesson_teacher)
    # lessons = relationship("LessonModel", back_populates="teacher", lazy="joined", uselist=True,
    #                        secondary=AT_lesson_teacher)

    def __repr__(self):
        return f'<TeacherModel:\n' \
               f' guid: {self.guid}\n' \
               f' online_url: {self.online_url}\n' \
               f' alt_online_url: {self.alt_online_url}\n' \
               f' trans: {None if not self.trans else self.trans[0]}>'
