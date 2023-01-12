from typing import Optional

from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session

from backend.Schemas.Academic import Academic, AcademicOutput


class GroupBase(BaseModel):
    name: str = Field(description="Название группы")
    course: int = Field(description="Курс обучения")


class GroupCreate(GroupBase):
    academic: Optional[str] = Field(description="Ученое звание")


class GroupOutput(GroupBase):

    class Config:
        orm_mode = True


class Group(GroupBase):
    guid: UUID4 = Field(description="ID")
    academic: AcademicOutput = Field(description="Ученое звание")

    class Config:
        orm_mode = True
