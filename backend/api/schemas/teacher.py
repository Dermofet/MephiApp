from typing import Optional

from pydantic import ConfigDict, UUID4, BaseModel, Field


class TeacherBaseSchema(BaseModel):
    lang: str = Field(description="Код страны (для перевода)")
    name: str = Field(description="ФИО приподавателя")
    fullname: Optional[str] = Field(description="Полное ФИО преподавателя")


class TeacherCreateSchema(TeacherBaseSchema):
    pass


class TeacherOutputSchema(TeacherBaseSchema):
    pass


class TeacherSchema(TeacherBaseSchema):
    guid: Optional[UUID4] = Field(description="ID")
    model_config = ConfigDict(from_attributes=True)
