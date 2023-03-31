import copy
import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.connection import Base


class TeacherTranslateModel(Base):
    __tablename__ = "teacher_translate"
    __table_args__ = {'extend_existing': True}

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    name = Column(String)
    fullname = Column(String, unique=True, nullable=True)
    lang = Column(String(2))
    teacher_guid = Column(UUID(as_uuid=True), ForeignKey("teachers.guid"))

    teacher = relationship("TeacherModel", back_populates="trans", lazy="joined", uselist=False,
                           primaryjoin="TeacherTranslateModel.teacher_guid == TeacherModel.guid")

    def __repr__(self):
        return f'<TeacherTranslateModel: {self.name}\n>'
