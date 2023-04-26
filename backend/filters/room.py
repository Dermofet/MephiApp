from datetime import date, time
from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field


class RoomFilter(Filter):
    time_start: time = Field(description="Начало отрезка времени, в котором аудитория свободна")
    time_end: time = Field(description="Конец отрезка времени, в котором аудитория свободна")
    corps: str = Field(description="Корпус, в которой находится аудитория")
    date_: date = Field(description="Дата, когда аудитория свободна")

    def __repr__(self):
        return f'RoomFilter:\n' \
               f'  time_start = {self.time_start}\n' \
               f'  time_end = {self.time_end}\n' \
               f'  corps = {self.corps}\n' \
               f'  date = {self.date}\n' \
               f'  week = {self.date}'
