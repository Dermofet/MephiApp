import os

import icalendar

from etl.parsers.base_parser import BaseParser
from etl.schemas.start_semester import StartSemesterLoading


class StartSemesterParser(BaseParser):
    url: str

    def __init__(
        self,
        url: str,
        redis: str,
        use_auth: bool,
        single_connection_client: bool = True,
        is_logged: bool = True,
    ):
        super().__init__(
            use_auth=use_auth, redis=redis, single_connection_client=single_connection_client, is_logged=is_logged
        )
        self.url = url

    async def parse(self):
        download_url = await self.__get_download_url()

        filepath = f"{os.getcwd()}/tmp.ics"
        await self.download_file_with_auth(download_url, filepath)
        date = self.__parse_date(filepath)
        os.remove(filepath)

        self.__set_info_to_db(date)

    async def __get_download_url(self):
        soup = await self.soup(self.url)
        schedule_url = (
            self.base_url(self.url) + soup.find("a", class_="list-group-item text-center text-nowrap")["href"]
        )

        soup = await self.soup(schedule_url)
        return self.base_url(self.url) + soup.findAll("a", class_="btn btn-primary btn-outline")[-1]["href"]

    def __parse_date(self, path: str):
        with open(path, "rb") as file:
            cal = icalendar.Calendar.from_ical(file.read())

        dates = []

        for event in cal.walk("VEVENT"):
            start = event.get("DTSTART").dt
            dates.append(start)

        min_date = min(dates).date()
        self.logger.info(f"Дата начала семестра: {min_date}")

        return StartSemesterLoading(date=min_date)

    def __set_info_to_db(self, date_: StartSemesterLoading):
        self.db.set(name="start_semester", value=date_.model_dump_redis())
