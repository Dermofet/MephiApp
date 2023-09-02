from typing import List

from etl.parsers.base_parser import BaseParser
from etl.schemas.corps import CorpsLoading
from etl.schemas.room import RoomLoading


class RoomParser(BaseParser):
    url: str

    def __init__(
            self,
            url: str,
            redis_host: str,
            redis_port: int,
            db: int,
            single_connection_client: bool = True,
            is_logged: bool = True,
    ):
        super().__init__(redis_host, redis_port, db, single_connection_client, is_logged)
        self.url = url

        self.logger.info('RoomParser initialized')

    async def parse(self):
        res_rooms, res_corps = await self.parse_rooms()
        self.set_info_to_db(res_rooms, res_corps)

    async def parse_rooms(self):
        soup = await self.soup(self.url)

        res_rooms = []
        res_corps = []

        box = soup.find("div", class_="box")
        for name, rooms in zip(box.findAll("h3", class_="light"), box.findAll("ul", class_="list-inline")):
            res_corps.append(CorpsLoading(name=name.text))
            res_rooms.extend(
                RoomLoading(name=room.text, corps=name.text)
                for room in rooms.findAll("a")
            )

        self.logger.info(f'Rooms found: {len(res_rooms)}\nCorps found: {len(res_corps)}')

        return res_rooms, res_corps

    def set_info_to_db(self, rooms: List[RoomLoading], corps: List[CorpsLoading]):
        for corp in corps:
            self.db.hset("corps", hash(corp), corp.model_dump())

        for room in rooms:
            self.db.hset("rooms", hash(room), room.model_dump())
