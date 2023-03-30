from datetime import date as Date
from datetime import time
from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field


class RoomFilter(Filter):
    time_start: time = Field(description="Начало отрезка времени, в котором аудитория свободна")
    time_end: time = Field(description="Конец отрезка времени, в котором аудитория свободна")
    corps: str = Field(description="Корпус, в которой находится аудитория")
    date: Date = Field(description="Дата, когда аудитория свободна")
    week: int = Field(description="Четность недели")