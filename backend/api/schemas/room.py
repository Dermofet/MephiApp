from typing import Optional

from pydantic import UUID4, BaseModel, Field

from backend.database.models.room import RoomModel
from backend.schemas.corps import CorpsOutputSchema, CorpsSchema


class RoomBaseSchema(BaseModel):
    number: str = Field(description="Номер аудитории")


class RoomCreateSchema(RoomBaseSchema):
    corps: Optional[str] = Field(description="Корпус, в котором находится аудитория")


class RoomOutputSchema(RoomBaseSchema):
    corps: CorpsOutputSchema = Field(description="Корпус, в котором находится аудитория")


class RoomSchema(RoomBaseSchema):
    guid: Optional[UUID4] = Field(description="ID аудитории")
    corps: CorpsSchema = Field(description="Корпус, в котором находится аудитория")

    def clone(self):
        return RoomSchema(
            guid=self.guid,
            number=self.number,
            corps=self.corps.clone()
        )

    def to_model(self):
        return RoomModel(
            guid=self.guid,
            number=self.number,
            corps_guid=self.corps.guid,
            corps=self.corps.to_model() if self.corps.guid is None else None
        )

    def __eq__(self, other):
        if isinstance(other, RoomSchema):
            return self.number == other.number
        return False

    def __hash__(self):
        return hash(self.number)

    class Config:
        orm_mode = True
