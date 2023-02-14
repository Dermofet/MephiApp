from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session


class AcademicBaseSchema(BaseModel):
    name: str = Field(description="Ученое звание")


class AcademicCreateSchema(AcademicBaseSchema):
    pass


class AcademicOutputSchema(AcademicBaseSchema):
    pass


class AcademicSchema(AcademicBaseSchema):
    guid: UUID4 = Field(description="ID")

    class Config:
        orm_mode = True
