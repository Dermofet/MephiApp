import uuid

from app.backend.database.connection import Base
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class TeacherTranslateModel(Base):
    __tablename__ = "teacher_translate"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    name = Column(String, unique=True)
    fullname = Column(String, unique=True, nullable=True)
    lang = Column(String(2))
    teacher_guid = Column(UUID(as_uuid=True), ForeignKey("teachers.guid"))

    teacher = relationship("TeacherModel", back_populates="trans", lazy="joined", uselist=False,
                           primaryjoin="TeacherTranslateModel.teacher_guid == TeacherModel.guid")

    def __repr__(self):
        return f'<TeacherTranslateModel:\n' \
               f' guid: {self.guid}\n' \
               f' name: {self.name}\n' \
               f' fullname: {self.fullname}\n' \
               f' lang: {self.lang}\n' \
               f' teacher_guid: {self.teacher_guid}>'
