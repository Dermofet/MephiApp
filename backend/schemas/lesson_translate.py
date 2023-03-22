from copy import deepcopy
from typing import Optional

from pydantic import UUID4, BaseModel, Field, validator
from sqlalchemy.orm import Session

from backend.database.models.lesson_translate import LessonTranslateModel


class LessonTranslateBaseSchema(BaseModel):
    type: Optional[str] = Field(description="Тип занятия")
    name: str = Field(description="Название занятия")
    subgroup: Optional[str] = Field(description="Обозначение подгруппы (если имеется)")
    lang: str = Field(description="Код языка")


class LessonTranslateCreateSchema(LessonTranslateBaseSchema):
    lesson_guid: UUID4 = Field(description="ID занятия")


class LessonTranslateOutputSchema(LessonTranslateBaseSchema):
    pass


class LessonTranslateSchema(LessonTranslateBaseSchema):
    guid: Optional[UUID4] = Field(description="ID")

    def clone(self):
        return LessonTranslateSchema(
            guid=self.guid,
            type=self.type,
            name=self.name,
            subgroup=self.subgroup,
            lang=self.lang
        )

    def to_model(self):
        return LessonTranslateModel(
            guid=self.guid,
            type=self.type,
            name=self.name,
            subgroup=self.subgroup,
            lang=self.lang
        )

    def __eq__(self, other):
        if isinstance(other, LessonTranslateModel):
            return self.name == other.name and self.type == other.type and self.lang == other.lang and \
                   self.subgroup == other.subgroup
        return False

    def __hash__(self):
        return hash(str(self.name) + str(self.subgroup) + str(self.lang) + str(self.type))

    class Config:
        orm_mode = True
