from typing import Optional

from pydantic import UUID4, BaseModel, Field, validator
from sqlalchemy.orm import Session


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
    guid: UUID4 = Field(description="ID")

    class Config:
        orm_mode = True
