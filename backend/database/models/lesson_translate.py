import copy
import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.connection import Base
from backend.database.models.association_tables import *


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

    def __eq__(self, other):
        if isinstance(other, LessonTranslateModel):
            return self.name == other.name and self.type == other.type and self.lang == other.lang and \
                   self.subgroup == other.subgroup
        return False

    def __hash__(self):
        return hash(str(self.name) + str(self.subgroup) + str(self.lang) + str(self.type))

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result
