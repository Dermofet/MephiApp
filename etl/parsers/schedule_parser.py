import asyncio
from copy import deepcopy
from typing import List

from etl.parsers.base_parser import BaseParser
from etl.schemas.lesson import LessonLoading


class ScheduleParser(BaseParser):
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

    async def parse(self):
        self.logger.info("Start etl schedule")

        for academic_name, academic_url in await self.get_academic_types():
            groups_info = await self.get_groups_info(academic_name, academic_url)

            self.logger.info(f'{academic_name} was parsed')

            await self.set_info_to_db(groups_info)

        self.logger.info("All lessons set in the redis")


    async def get_academic_types(self):
        soup = await self.soup(self.url)

        res = []
        base_url = self.base_url(self.url)
        for item in soup.findAll("ul", class_="nav nav-tabs btn-toolbar"):
            elems = item.findAll("a")
            res.extend(
                (elem['title'], f'{base_url}{elem["href"]}')
                for elem in elems
                if elem['href'] != "#"
            )

        self.logger.info(f'Found {len(res)} academic types')
        return res

    async def get_groups_info(self, name: str, url: str):
        soup = await self.soup(url)

        base_url = self.base_url(url)

        courses = soup.findAll("div", class_="list-group")
        tasks = []
        for groups, i in zip(courses, range(len(courses))):
            tasks.extend(
                self.get_group_info(
                    url=f"{base_url}{item['href']}",
                    academic=name,
                    group=item.text.strip(),
                    course=i + 1,
                    lang="ru",
                )
                for item in groups.findAll("a")
            )

        self.logger.debug(f"Created {len(tasks)} tasks")

        return await asyncio.gather(*tasks)

    async def get_group_info(self, url, academic, group, course, lang):
        soup = await self.soup(url)
        self.logger.debug(f"Parsing group: {group}, course: {course}, academic: {academic}")

        schedule = []
        for lessons, day in zip(soup.find_all("div", class_="list-group"), self.get_weekdays(soup)):
            for lesson in lessons.find_all("div", class_="list-group-item"):
                schedule_elem = self.extract_schedule_element(lesson, academic, group, course, lang, day)
                schedule.append(deepcopy(schedule_elem))

        return schedule

    @staticmethod
    def get_weekdays(soup):
        return [day.text.strip() for day in soup.find_all("h3", class_="lesson-wday")]

    def extract_schedule_element(self, lesson, academic, group, course, lang, day):
        time_start, time_end = self.extract_time(lesson)
        dot, room = self.extract_room(lesson)
        lesson_type = self.extract_lesson_type(lesson)
        weeks = self.extract_weeks(lesson)
        teachers = self.extract_teachers(lesson)
        date_start, date_end = self.extract_dates(lesson)
        lesson_name, subgroup = self.extract_lesson_info(lesson)

        return LessonLoading(
            academic=academic,
            group=group,
            course=course,
            lang=lang,
            weekday=day,
            time_start=time_start,
            time_end=time_end,
            type=lesson_type,
            weeks=weeks,
            date_start=date_start,
            date_end=date_end,
            teachers=teachers,
            name=lesson_name,
            subgroup=subgroup,
            dot=dot,
            room=room,
        )

    @staticmethod
    def extract_time(lesson):
        time = lesson.find("div", class_="lesson-time").text.split(' — ')
        return time[0].strip(), time[1].strip() if len(time) == 2 else None

    @staticmethod
    def extract_room(lesson):
        room_div = lesson.find("div", class_="pull-right")
        if len(room_div.contents) != 3:
            return False, room_div.find("a", class_="text-nowrap").text
        return True, None

    @staticmethod
    def extract_lesson_type(lesson):
        lesson_type = lesson.find("div", class_="label label-default label-lesson")
        change_types = {
            "Пр": "практика",
            "Лек": "лекция",
            "Лаб": "лабораторная работа",
            "Ауд": "аудиторная работа"
        }
        return change_types.get(lesson_type.text) if lesson_type else None

    @staticmethod
    def extract_weeks(lesson):
        weeks = lesson.find("span", recursive=False)
        class_mapping = {
            "lesson-square-0": 2,
            "lesson-square-1": 1,
            "lesson-square-2": 0
        }
        return class_mapping.get(weeks["class"][1])

    @staticmethod
    def extract_teachers(lesson):
        return [
            teacher.find("a").text.replace(' ', '')
            for teacher in lesson.find_all("span", class_="text-nowrap")
        ]

    def extract_dates(self, lesson):
        if dates := lesson.find("span", class_="lesson-dates"):
            date_start, date_end = self.parse_date_range(dates.text)
            return date_start, date_end
        return None, None

    @staticmethod
    def extract_lesson_info(lesson):
        stripped_strings = list(lesson.stripped_strings)
        lesson_name = stripped_strings[0]
        subgroup = stripped_strings[1] if len(stripped_strings) > 1 and stripped_strings[1] != ',' else None
        return lesson_name, subgroup

    @staticmethod
    def parse_date_range(date_range):
        dates = date_range.replace(', ', ' — ').replace('\n(', '').replace(')\n', '').split(' — ')
        date_start = dates[0]
        date_end = dates[1] if len(dates) > 1 else None
        return date_start, date_end

    async def set_info_to_db(self, lessons: List[LessonLoading]):
        for lesson in lessons:
            self.db.hset(name="lessons", key=hash(lesson), value=lesson.model_dump())
