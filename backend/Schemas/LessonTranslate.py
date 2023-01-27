from typing import Optional

from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session

# from backend.Schemas.Language import Language


class LessonTranslateBase(BaseModel):
    type: str = Field(description="Тип занятия")
    name: str = Field(description="Название занятия")
    subgroup: Optional[str] = Field(description="Обозначение подгруппы (если имеется)")
    lang: str = Field(description="Код языка")


class LessonTranslateCreate(LessonTranslateBase):
    lesson_guid: UUID4 = Field(description="ID занятия")


class LessonTranslateOutput(LessonTranslateBase):
    pass


class LessonTranslate(LessonTranslateBase):
    guid: UUID4 = Field(description="ID")

    class Config:
        orm_mode = True
