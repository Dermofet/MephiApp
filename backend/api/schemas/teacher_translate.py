from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field


class TeacherTranslateBaseSchema(BaseModel):
    lang: str = Field(description="Код страны (для перевода)")
    name: str = Field(description="ФИО приподавателя")
    fullname: Optional[str] = Field(description="Полное ФИО преподавателя")


class TeacherTranslateCreateSchema(TeacherTranslateBaseSchema):
    teacher_guid: Optional[UUID4] = Field(description="ID преподавателя")


class TeacherTranslateOutputSchema(TeacherTranslateBaseSchema):
    pass


class TeacherTranslateSchema(TeacherTranslateBaseSchema):
    guid: Optional[UUID4] = Field(description="ID")
    model_config = ConfigDict(from_attributes=True)
