import uuid

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.connection import Base
from backend.database.models.association_tables import AT_lesson_group


class GroupModel(Base):
    __tablename__ = "groups"
    __table_args__ = {'extend_existing': True}

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    name = Column(String(10), unique=True)
    course = Column(Integer)
    academic_guid = Column(UUID(as_uuid=True), ForeignKey("academics.guid"))

    academic = relationship("AcademicModel", back_populates="groups", lazy="joined")
    lessons = relationship("LessonModel", back_populates="groups", lazy="joined", uselist=True,
                           secondary=AT_lesson_group)

    def __repr__(self):
        return f'<GroupModel:\n' \
               f' guid: {self.guid}\n' \
               f' name: {self.name}\n' \
               f' course: {self.course}\n' \
               f' academic_guid: {self.academic_guid}>'
