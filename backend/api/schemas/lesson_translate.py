from typing import Optional

from pydantic import ConfigDict, UUID4, BaseModel, Field

from backend.api.database.models.lesson_translate import LessonTranslateModel


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
    model_config = ConfigDict(from_attributes=True)
