from dataclasses import dataclass
from datetime import date, time


@dataclass
class RoomFilter:
    time_start: time
    time_end: time
    date_: date
