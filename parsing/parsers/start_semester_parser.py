import os
from datetime import datetime

import bs4
import icalendar
import requests

from backend.database.connection import get_session_return
from backend.schemas.start_semester import StartSemesterCreateSchema
from backend.services.start_semester import StartSemesterService
from parsing import config


def get_download_url():
    html = requests.get(config.MEPHI_SCHEDULE_URL).content
    soup = bs4.BeautifulSoup(html, 'lxml')

    schedule_url = config.HOME_MEPHI_URL + soup.find("a", class_="list-group-item text-center text-nowrap")['href']

    html = requests.get(schedule_url).content
    soup = bs4.BeautifulSoup(html, 'lxml')

    download_url = config.HOME_MEPHI_URL + soup.findAll("a", class_="btn btn-primary btn-outline")[-1]['href']
    return download_url


def download_ics(url: str, path: str):
    response = requests.get(url)
    with open(path, 'wb') as file:
        file.write(response.content)


def parse_date(path: str):
    with open(path, 'rb') as file:
        cal = icalendar.Calendar.from_ical(file.read())

    dates = []

    for event in cal.walk('VEVENT'):
        start = event.get('DTSTART').dt
        dates.append(start)

    min_date = min(dates)
    print('Минимальная дата:', min_date)

    return min_date


async def insert_date(date: datetime.date):
    db = await get_session_return()
    await StartSemesterService.update(db, StartSemesterCreateSchema(date=date))
    await db.close()


async def start_parse():
    download_url = get_download_url()
    filepath = f'{os.getcwd()}/tmp.ics'
    download_ics(download_url, filepath)
    date = parse_date(filepath)
    os.remove(filepath)
    await insert_date(date)
