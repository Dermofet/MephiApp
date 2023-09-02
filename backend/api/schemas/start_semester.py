import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, Field

from backend.database.models.start_semester import StartSemesterModel


class StartSemesterBaseSchema(BaseModel):
    date: datetime.date = Field(description="Дата начала семестра")

    class Config:
        orm_mode = True


class StartSemesterCreateSchema(StartSemesterBaseSchema):
    pass


class StartSemesterOutputSchema(StartSemesterBaseSchema):
    pass


class StartSemesterSchema(StartSemesterBaseSchema):
    guid: Optional[UUID4] = Field(description="ID")

