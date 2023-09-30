from pydantic import BaseModel, Field

from etl.schemas.base import Base


class GroupLoading(Base):
    name: str = Field(description="Название группы")
    course: int = Field(description="Курс обучения")
    academic: str = Field(description="Ученое звание")

    def __eq__(self, other) -> bool:
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)