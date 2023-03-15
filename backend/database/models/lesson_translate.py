import uuid

from app.backend.database.connection import Base
from app.backend.database.models.association_tables import *
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class LessonTranslateModel(Base):
    __tablename__ = "lesson_translate"

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True, unique=True)
    type = Column(String(10), nullable=True)
    name = Column(String)
    subgroup = Column(String(200), nullable=True)
    lang = Column(String(2))
    lesson_guid = Column(UUID(as_uuid=True), ForeignKey("lessons.guid"))

    lesson = relationship("LessonModel", back_populates="trans", lazy="joined", uselist=False,
                          primaryjoin="LessonTranslateModel.lesson_guid == LessonModel.guid")

    def __repr__(self):
        return f'<LessonTranslateModel:\n' \
               f' guid: {self.guid}\n' \
               f' type: {self.type}\n' \
               f' name: {self.name}\n' \
               f' subgroup: {self.subgroup}\n' \
               f' lang: {self.lang}\n' \
               f' lesson_guid: {self.lesson_guid}>'
