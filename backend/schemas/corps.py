from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session


class CorpsBaseSchema(BaseModel):
    name: str = Field(description="Название корпуса")


class CorpsCreateSchema(CorpsBaseSchema):
    pass


class CorpsOutputSchema(CorpsBaseSchema):
    pass


class CorpsSchema(CorpsBaseSchema):
    guid: UUID4 = Field(description="ID")

    class Config:
        orm_mode = True
