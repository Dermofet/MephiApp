from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session

from backend.Schemas.Corps import CorpsOutput


class RoomBase(BaseModel):
    number: str = Field(description="Номер аудитории")


class RoomCreate(RoomBase):
    pass


class RoomOutput(RoomBase):
    corps: CorpsOutput = Field(description="Корпус, в котором находится аудитория")

    class Config:
        orm_mode = True


class Room(RoomBase):
    guid: UUID4 = Field(description="ID аудитории")
    corps: CorpsOutput = Field(description="Корпус, в котором находится аудитория")

    class Config:
        orm_mode = True
