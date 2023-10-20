import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field


class StartSemesterBaseSchema(BaseModel):
    date: datetime.date = Field(description="Дата начала семестра")
    model_config = ConfigDict(from_attributes=True)


class StartSemesterCreateSchema(StartSemesterBaseSchema):
    pass


class StartSemesterOutputSchema(StartSemesterBaseSchema):
    pass


class StartSemesterSchema(StartSemesterBaseSchema):
    guid: Optional[UUID4] = Field(description="ID")
