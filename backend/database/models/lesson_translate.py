import uuid

from backend.database.models.association_tables import *


class LessonTranslateModel(Base):
    __tablename__ = "lesson_translate"
    __table_args__ = {'extend_existing': True}

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    type = Column(String(50), nullable=True)
    name = Column(String)
    subgroup = Column(String(200), nullable=True)
    lang = Column(String(2))
    lesson_guid = Column(UUID(as_uuid=True), ForeignKey("lessons.guid"))

    lesson = relationship("LessonModel", back_populates="trans", lazy="joined", uselist=False,
                          primaryjoin="LessonTranslateModel.lesson_guid == LessonModel.guid")

    def __repr__(self):
        return f'<LessonTranslateModel:\n' \
               f' type: {self.type}\n' \
               f' name: {self.name}\n' \
               f' subgroup: {self.subgroup}\n' \
               f' lang: {self.lang}>'
