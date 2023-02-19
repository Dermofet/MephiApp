from typing import Optional

from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session


class TeacherTranslateBaseSchema(BaseModel):
    name: str = Field(description="Краткое ФИО")
    fullname: Optional[str] = Field(description="Полное ФИО")
    lang: str = Field(description="Код языка")


class TeacherTranslateCreateSchema(TeacherTranslateBaseSchema):
    teacher_guid: UUID4 = Field(description="ID преподавателя")


class TeacherTranslateOutputSchema(TeacherTranslateBaseSchema):
    pass


class TeacherTranslateSchema(TeacherTranslateBaseSchema):
    guid: UUID4 = Field(description="ID")

    class Config:
        orm_mode = True
