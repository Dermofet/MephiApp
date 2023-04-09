import asyncio
import json
import os.path
import sys
from copy import deepcopy

import aiohttp
import bs4
import requests

from parsing import config


class ScheduleParser:
    def __init__(self):
        self.config = config

    async def parse_schedule(self):
        async with aiohttp.ClientSession() as session:
            for academic_name, academic_url in await self.getAcademicTypes(session):
                print(f'{academic_name}:')
                groups_list = await self.getGroupList(session, academic_url)
                await self.setInfoToFile(session, groups_list, f'{os.getcwd()}/parsing/schedule/{academic_name}.json', mode='w',
                                         encoding='utf-8', indent=3, ensure_ascii=False)

    async def getAcademicTypes(self, session):
        async with session.get(self.config.MEPHI_SCHEDULE_URL) as response:
            html = await response.text()
        soup = bs4.BeautifulSoup(html, "lxml")
        res = []
        for item in soup.findAll("ul", class_="nav nav-tabs btn-toolbar"):
            elems = item.findAll("a")
            for elem in elems:
                if elem['href'] != "#":
                    res.append((elem['title'], f'{self.config.HOME_MEPHI_URL}{elem["href"]}'))
        return res

    async def getGroupList(self, session, url: str):
        async with session.get(url) as response:
            html = await response.text()
        soup = bs4.BeautifulSoup(html, "lxml")
        res = []
        courses = soup.findAll("div", class_="list-group")
        for groups, i in zip(courses, range(len(courses))):
            res.append({"course": i + 1, "groups": []})
            items_a = groups.findAll("a")
            for item in items_a:
                res[i]["groups"].append({"name": item.text.strip(), "url": self.config.HOME_MEPHI_URL + item['href']})
        return res

    @staticmethod
    async def getGroupInfo(session, url: str, academic, group, course, lang):
        async with session.get(url) as response:
            html = await response.text()
        soup = bs4.BeautifulSoup(html, "lxml")

        print(f'  {group}')
        weekdays = [day.text.strip() for day in soup.findAll("h3", class_="lesson-wday")]
        schedule = []
        for lessons, day in zip(soup.findAll("div", class_="list-group"), weekdays):
            for lesson in lessons.findAll("div", class_="list-group-item"):
                for elem in lesson.find("div", class_="lesson-lessons").findAll("div", recursive=False):
                    schedule_elem = {
                        'academic': academic,
                        'group': group,
                        'course': course,
                        'lang': lang
                    }

                    time = lesson.find("div", class_="lesson-time").text.split(' — ')
                    schedule_elem['time_start'] = time[0].strip()
                    schedule_elem['time_end'] = time[1].strip() if len(time) == 2 else None

                    if len(elem.find("div", class_="pull-right").contents) == 3:
                        schedule_elem['dot'] = True
                        schedule_elem['room'] = None
                    else:
                        schedule_elem['dot'] = False
                        schedule_elem['room'] = elem.find("div", class_="pull-right").find("a",
                                                                                           class_="text-nowrap").text
                    lesson_type = elem.find("div", class_="label label-default label-lesson")
                    change_types = {
                        "Пр": "практика",
                        "Лек": "лекция",
                        "Лаб": "лабораторная работа",
                        "Ауд": "аудиторная работа"
                    }
                    schedule_elem['lesson_type'] = change_types[lesson_type.text] if lesson_type else None

                    weeks = elem.find("span", recursive=False)
                    if weeks["class"][1] == "lesson-square-0":
                        schedule_elem["weeks"] = 2
                    elif weeks["class"][1] == "lesson-square-1":
                        schedule_elem["weeks"] = 1
                    elif weeks["class"][1] == "lesson-square-2":
                        schedule_elem["weeks"] = 0

                    schedule_elem['teacher_name'] = []
                    for teacher in elem.findAll("span", class_="text-nowrap"):
                        schedule_elem['teacher_name'].append(teacher.find("a").text.replace(' ', ' '))

                    schedule_elem["date_start"] = None
                    schedule_elem["date_end"] = None
                    dates = elem.find("span", class_="lesson-dates")
                    if dates:
                        date = dates.text.replace(', ', ' — ').split(' — ')
                        if len(date) == 1:
                            schedule_elem["date_start"] = date[0].replace('\n(', '').replace(')\n', '')
                            schedule_elem["date_end"] = None
                        else:
                            schedule_elem["date_start"] = date[0].replace('\n(', '').replace(')\n', '')
                            schedule_elem["date_end"] = date[1].replace('\n(', '').replace(')\n', '')

                    for x in elem.select('div, span, i'):
                        x.decompose()

                    strings = [text for text in elem.stripped_strings]
                    schedule_elem['lesson_name'] = strings[0]

                    if len(strings) == 1:
                        schedule_elem['subgroup'] = None
                    else:
                        if strings[1] != ',':
                            schedule_elem['subgroup'] = strings[1]
                        else:
                            schedule_elem['subgroup'] = None

                    schedule.append(deepcopy(schedule_elem))
        return schedule

    async def setInfoToFile(self, session, dict_json, filename, mode, encoding, indent, ensure_ascii):
        tasks = []
        for course in dict_json:
            for group in course["groups"]:
                tasks.append(self.getGroupInfo(session, group["url"], filename.split("/")[-1].split(".")[0], group,
                                               course, "ru"))

        print(f"Total groups: {len(tasks)}")
        lessons = await asyncio.gather(*tasks)

        res = []
        for lesson in lessons:
            res += lesson

        print("Parsing completed")

        with open(filename, mode, encoding=encoding) as fp:
            json.dump(res, fp=fp, indent=indent, ensure_ascii=ensure_ascii)
