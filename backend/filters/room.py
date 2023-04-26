from datetime import date, time
from typing import List, Optional

from fastapi import Query
from fastapi_filter.contrib.sqlalchemy import Filter

# from pydantic import Field


class RoomFilter(Filter):
    time_start: time = Query(..., description="Начало отрезка времени, в котором аудитория свободна")
    time_end: time = Query(..., description="Конец отрезка времени, в котором аудитория свободна")
    corps: List[str] = Query([], description="Корпусы, в которых находятся аудитории")
    date_: date = Query(..., description="Дата, когда аудитория свободна")

    def __repr__(self):
        return f'RoomFilter:\n' \
               f'  time_start = {self.time_start}\n' \
               f'  time_end = {self.time_end}\n' \
               f'  corps = {self.corps}\n' \
               f'  date = {self.date}\n' \
               f'  week = {self.date}'
