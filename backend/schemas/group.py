from typing import Optional

from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session

from backend.schemas.academic import AcademicOutputSchema, AcademicSchema


class GroupBaseSchema(BaseModel):
    name: str = Field(description="Название группы")
    course: int = Field(description="Курс обучения")


class GroupCreateSchema(GroupBaseSchema):
    academic: str = Field(description="Ученое звание")


class GroupOutputSchema(GroupBaseSchema):
    academic: AcademicOutputSchema = Field(description="Ученое звание")


class GroupSchema(GroupBaseSchema):
    guid: UUID4 = Field(description="ID")
    academic: AcademicSchema = Field(description="Ученое звание")

    class Config:
        orm_mode = True
