import uuid

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.connection import Base
from backend.database.models.association_tables import AT_lesson_teacher


class TeacherModel(Base):
    __tablename__ = "teachers"
    __table_args__ = {'extend_existing': True}

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    online_url = Column(String, nullable=True, unique=True)
    alt_online_url = Column(String, nullable=True, unique=True)

    trans = relationship("TeacherTranslateModel", back_populates="teacher", lazy="joined", uselist=True,
                         primaryjoin="TeacherModel.guid == TeacherTranslateModel.teacher_guid")
    lessons = relationship("LessonModel", back_populates="teachers", lazy="joined", uselist=True,
                           secondary=AT_lesson_teacher)

    def __repr__(self):
        return f'<TeacherModel: {None if not self.trans else self.trans[0]}>'

    def __eq__(self, other):
        if isinstance(other, TeacherModel):
            return self.trans[0].name == other.trans[0].name and self.trans[0].fullname == other.trans[0].fullname and \
                   self.trans[0].lang == self.trans[0].lang
        return False

    def __hash__(self):
        return hash(str(self.trans[0].name) + str(self.trans[0].fullname) + str(self.trans[0].lang))