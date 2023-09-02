from datetime import date, time
from typing import Annotated, Union

from fastapi import Depends, Query
from fastapi_filter.contrib.sqlalchemy import Filter


class RoomFilter(Filter):
    time_start: time = Query(..., description="Начало отрезка времени, в котором аудитория свободна")
    time_end: time = Query(..., description="Конец отрезка времени, в котором аудитория свободна")
    date_: date = Query(..., description="Дата, когда аудитория свободна")

    def __repr__(self):
        return f'RoomFilter:\n' \
               f'  time_start = {self.time_start}\n' \
               f'  time_end = {self.time_end}\n' \
               f'  corps = {self.corps}\n' \
               f'  date = {self.date}\n' \
               f'  week = {self.date}'