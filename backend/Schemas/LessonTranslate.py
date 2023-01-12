from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session

from backend.Schemas.Language import Language


class LessonTranslateBase(BaseModel):
    type: str = Field(description="Тип занятия")
    name: str = Field(description="Название занятия")
    subgroup: str = Field(description="Обозначение подгруппы (если имеется)")


class LessonTranslateCreate(LessonTranslateBase):
    pass


class LessonTranslateOutput(LessonTranslateBase):

    class Config:
        orm_mode = True


class LessonTranslate(LessonTranslateBase):
    guid: UUID4 = Field(description="ID")
    lang: Language = Field(description="Код языка")

    class Config:
        orm_mode = True
