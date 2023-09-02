from typing import Optional

from pydantic import Field
from etl.schemas.base import Base


class RoomLoading(Base):
    number: str = Field(description="Номер аудитории")
    corps: Optional[str] = Field(description="Корпус, в котором находится аудитория")

    def __hash__(self):
        return hash(self.number)

    def __eq__(self, other):
        return self.number == other.number