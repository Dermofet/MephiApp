from typing import Optional

from pydantic import ConfigDict, UUID4, BaseModel, Field

from backend.api.schemas.teacher_translate import TeacherTranslateBaseSchema, TeacherTranslateCreateSchema, TeacherTranslateOutputSchema, TeacherTranslateSchema


class TeacherBaseSchema(BaseModel):
    url: Optional[str] = Field(description="Ссылка на дискорд")
    alt_url: Optional[str] = Field(description="Ссылка на дискорд") 


class TeacherCreateSchema(TeacherBaseSchema):
    trans: list[TeacherTranslateCreateSchema] = Field(description="Список преподавателей")


class TeacherOutputSchema(TeacherBaseSchema):
    trans: list[TeacherTranslateOutputSchema] = Field(description="Список преподавателей")


class TeacherSchema(TeacherBaseSchema):
    guid: Optional[UUID4] = Field(description="ID")
    model_config = ConfigDict(from_attributes=True)

    trans: list[TeacherTranslateSchema] = Field(description="Список преподавателей")
