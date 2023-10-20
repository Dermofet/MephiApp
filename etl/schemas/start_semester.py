import datetime

from pydantic import Field

from etl.schemas.base import Base


class StartSemesterLoading(Base):
    date: datetime.date = Field(description="Дата начала семестра")
