from typing import List, Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field

from backend.api.schemas.teacher_translate import (
    TeacherTranslateCreateSchema,
    TeacherTranslateOutputSchema,
    TeacherTranslateSchema,
)


class TeacherBaseSchema(BaseModel):
    url: Optional[str] = Field(description="Ссылка на дискорд")
    alt_url: Optional[str] = Field(description="Ссылка на дискорд") 


class TeacherCreateSchema(TeacherBaseSchema):
    trans: List[TeacherTranslateCreateSchema] = Field(description="Список преподавателей")


class TeacherOutputSchema(TeacherBaseSchema):
    trans: List[TeacherTranslateOutputSchema] = Field(description="Список преподавателей")


class TeacherSchema(TeacherBaseSchema):
    guid: Optional[UUID4] = Field(description="ID")
    model_config = ConfigDict(from_attributes=True)

    trans: List[TeacherTranslateSchema] = Field(description="Список преподавателей")
