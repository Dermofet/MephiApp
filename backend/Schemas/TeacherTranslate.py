from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session

from backend.Schemas.Language import Language


class TeacherTranslateBase(BaseModel):
    name: str = Field(description="Краткое ФИО")
    fullname: str = Field(description="Полное ФИО")


class TeacherTranslateCreate(TeacherTranslateBase):
    pass


class TeacherTranslateOutput(TeacherTranslateBase):

    class Config:
        orm_mode = True


class TeacherTranslate(TeacherTranslateBase):
    guid: UUID4 = Field(description="ID")
    lang: Language = Field(description="Код языка")

    class Config:
        orm_mode = True
