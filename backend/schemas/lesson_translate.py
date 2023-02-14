from typing import Optional

from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session

from backend.schemas.lesson_without_language import LessonWithoutLanguageOutputSchema, LessonWithoutLanguageSchema


class LessonTranslateBaseSchema(BaseModel):
    type: Optional[str] = Field(description="Тип занятия")
    name: str = Field(description="Название занятия")
    subgroup: Optional[str] = Field(description="Обозначение подгруппы (если имеется)")
    lang: str = Field(description="Код языка")


class LessonTranslateCreateSchema(LessonTranslateBaseSchema):
    lesson_guid: UUID4 = Field(description="ID занятия")


class LessonTranslateOutputSchema(LessonTranslateBaseSchema):
    lesson: LessonWithoutLanguageOutputSchema = Field(description="Поля занятия, не нуждающиеся в переводе")


class LessonTranslateSchema(LessonTranslateBaseSchema):
    guid: UUID4 = Field(description="ID")
    lesson: LessonWithoutLanguageSchema = Field(description="Поля занятия, не нуждающиеся в переводе")

    class Config:
        orm_mode = True
