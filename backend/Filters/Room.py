from typing import Optional
from datetime import date, time

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import Field


class RoomFilter(Filter):
    time_start: Optional[time] = Field(description="Время, с которого аудитория будет заниматься")
    time_end: Optional[time] = Field(description="Время, до которого аудитория будет заниматься")
    _date: Optional[date] = Field(description="Дата, когда аудитори будет заниматься")
    corps: Optional[str] = Field(description="Корпус, где будет проводится поиск пустых аудиторий")
    week: Optional[int] = Field(description="Фильтр по неделям (по четным или нечетным неделям или все время)")
