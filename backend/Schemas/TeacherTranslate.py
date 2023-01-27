from typing import Optional

from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session

# from backend.Schemas.Language import Language


class TeacherTranslateBase(BaseModel):
    name: str = Field(description="Краткое ФИО")
    fullname: Optional[str] = Field(description="Полное ФИО")
    lang: str = Field(description="Код языка")


class TeacherTranslateCreate(TeacherTranslateBase):
    teacher_guid: UUID4 = Field(description="ID преподавателя")


class TeacherTranslateOutput(TeacherTranslateBase):
    pass


class TeacherTranslate(TeacherTranslateBase):
    guid: UUID4 = Field(description="ID")

    class Config:
        orm_mode = True
