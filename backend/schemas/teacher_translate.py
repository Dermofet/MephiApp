from typing import Optional

from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session

from backend.schemas.teacher import TeacherOutputSchema, TeacherSchema


class TeacherTranslateBaseSchema(BaseModel):
    name: str = Field(description="Краткое ФИО")
    fullname: Optional[str] = Field(description="Полное ФИО")
    lang: str = Field(description="Код языка")


class TeacherTranslateCreateSchema(TeacherTranslateBaseSchema):
    teacher_guid: UUID4 = Field(description="ID преподавателя")


class TeacherTranslateOutputSchema(TeacherTranslateBaseSchema):
    teacher: TeacherOutputSchema = Field(description="Поля преподавателя, не нуждающиеся в переводе")


class TeacherTranslateSchema(TeacherTranslateBaseSchema):
    guid: UUID4 = Field(description="ID")
    teacher: TeacherSchema = Field(description="Поля преподавателя, не нуждающиеся в переводе")

    class Config:
        orm_mode = True
