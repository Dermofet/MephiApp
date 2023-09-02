import datetime
from typing import Optional

from pydantic import ConfigDict, UUID4, BaseModel, Field


class StartSemesterBaseSchema(BaseModel):
    date: datetime.date = Field(description="Дата начала семестра")
    model_config = ConfigDict(from_attributes=True)


class StartSemesterCreateSchema(StartSemesterBaseSchema):
    pass


class StartSemesterOutputSchema(StartSemesterBaseSchema):
    pass


class StartSemesterSchema(StartSemesterBaseSchema):
    guid: Optional[UUID4] = Field(description="ID")

