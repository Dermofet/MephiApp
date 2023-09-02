import os

import bs4
import icalendar
import requests

from etl.parsers.base_parser import BaseParser
from etl.schemas.start_semester import StartSemesterLoading


class StartSemesterParser(BaseParser):
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

    def parse(self):
        download_url = self.__get_download_url()

        filepath = f'{os.getcwd()}/tmp.ics'
        self.__download_ics(download_url, filepath)
        date = self.__parse_date(filepath)
        os.remove(filepath)

        self.__set_info_to_db(date)


    # TODO: переместить def full_url() в BaseParser

    def __get_download_url(self):
        html = requests.get(self.url).content
        soup = bs4.BeautifulSoup(html, 'lxml')

        schedule_url = self.base_url(self.url) + soup.find("a", class_="list-group-item text-center text-nowrap")['href']

        html = requests.get(schedule_url).content
        soup = bs4.BeautifulSoup(html, 'lxml')

        return (
            self.base_url(self.url) + soup.findAll("a", class_="btn btn-primary btn-outline")[-1]['href']
        )

    @staticmethod
    def __download_ics(url: str, path: str):
        response = requests.get(url)
        with open(path, 'wb') as file:
            file.write(response.content)


    def __parse_date(self, path: str):
        with open(path, 'rb') as file:
            cal = icalendar.Calendar.from_ical(file.read())

        dates = []

        for event in cal.walk('VEVENT'):
            start = event.get('DTSTART').dt
            dates.append(start)

        min_date = min(dates)
        self.logger.info(f'Дата начала семестра: {min_date}')

        return StartSemesterLoading(date=min_date)

    def __set_info_to_db(self, date_: StartSemesterLoading):
        self.db.set("start_semester", date_.date.isoformat())
