from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session


class AcademicBase(BaseModel):
    name: str = Field(description="Ученое звание")


class AcademicCreate(AcademicBase):
    pass


class AcademicOutput(AcademicBase):

    class Config:
        orm_mode = True


class Academic(AcademicBase):
    guid: UUID4 = Field(description="ID")

    class Config:
        orm_mode = True
