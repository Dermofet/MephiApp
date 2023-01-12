from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session


class CorpsBase(BaseModel):
    name: str = Field(description="Название корпуса")


class CorpsCreate(CorpsBase):
    pass


class CorpsOutput(CorpsBase):

    class Config:
        orm_mode = True


class Corps(CorpsBase):
    id: UUID4 = Field(description="ID")

    class Config:
        orm_mode = True
