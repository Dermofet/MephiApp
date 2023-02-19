from datetime import date as Date
from datetime import time as Time
from typing import Optional

from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session

from backend.schemas.corps import CorpsOutputSchema, CorpsSchema


class RoomBaseSchema(BaseModel):
    number: str = Field(description="Номер аудитории")


class RoomCreateSchema(RoomBaseSchema):
    corps: Optional[str] = Field(description="Корпус, в котором находится аудитория")


class RoomOutputSchema(RoomBaseSchema):
    corps: CorpsOutputSchema = Field(description="Корпус, в котором находится аудитория")


class RoomSchema(RoomBaseSchema):
    guid: UUID4 = Field(description="ID аудитории")
    corps: CorpsSchema = Field(description="Корпус, в котором находится аудитория")

    class Config:
        orm_mode = True
