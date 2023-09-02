from pydantic import BaseModel, Field
from etl.schemas.base import Base


class GroupLoading(Base):
    name: str = Field(description="Название группы")
    course: int = Field(description="Курс обучения")
    academic: str = Field(description="Ученое звание")