import asyncio
from typing import List

from etl.parsers.base_parser import BaseParser
from etl.schemas.lesson import LessonExtracting


class ScheduleParser(BaseParser):
    url: str
    _index = 0

    def __init__(
            self,
            url: str,
            auth_url: str,
            auth_service_url: str,
            redis_host: str,
            redis_port: int,
            db: int,
            login: str,
            password: str,
            use_auth: bool,
            single_connection_client: bool = True,
            is_logged: bool = True,
    ):
        super().__init__(
            use_auth=use_auth,
            auth_url=auth_url,
            auth_service_url=auth_service_url,
            redis_host=redis_host, 
            redis_port=redis_port, 
            db=db,
            login=login,
            password=password,
            single_connection_client=single_connection_client, 
            is_logged=is_logged
        )
        self.url = url

    async def parse(self):
        self.logger.info("Start parsing schedule")

        for academic_name, academic_url in await self.__get_academic_types():
            groups_info = await self.__get_groups_info(academic_name, academic_url)

            self.logger.info(f'{academic_name} was parsed')

            await self.__set_info_to_db(groups_info)

        self.logger.info("All lessons set in the redis")

    async def __get_academic_types(self):
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

    async def __get_groups_info(self, name: str, url: str):
        soup = await self.soup(url)

        base_url = self.base_url(url)

        courses = soup.findAll("div", class_="list-group")
        tasks = []
        for groups, i in zip(courses, range(len(courses))):
            tasks.extend(
                self.__get_group_info(
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

    async def __get_group_info(self, url, academic, group, course, lang):
        soup = await self.soup(url)
        self.logger.debug(f"Parsing group: {group}, {course}, {academic}")

        schedule = []
        for lessons, day in zip(soup.find_all("div", class_="list-group"), self.__get_weekdays(soup)):
            for lesson in lessons.find_all("div", class_="list-group-item"):
                time_start, time_end = self.__extract_time(lesson)
                for lesson_item in lesson.find("div", class_="lesson-lessons").findChildren("div", recursive=False):
                    schedule_elem = self.__extract_schedule_element(
                        lesson_item,
                        academic,
                        group,
                        course,
                        lang,
                        day,
                        time_start,
                        time_end
                    )
                    schedule.append(schedule_elem.model_copy(deep=True))

        return schedule

    @staticmethod
    def __get_weekdays(soup):
        return [day.text.strip() for day in soup.find_all("h3", class_="lesson-wday")]

    def __extract_schedule_element(self, lesson, academic, group, course, lang, day, time_start, time_end):
        dot, room = self.__extract_room(lesson)
        lesson_type = self.__extract_lesson_type(lesson)
        weeks = self.__extract_weeks(lesson)
        teachers = self.__extract_teachers(lesson)
        date_start, date_end = self.__extract_dates(lesson)
        lesson_name, subgroup = self.__extract_lesson_info(lesson)

        return LessonExtracting(
            academic=academic,
            group=group,
            course=str(course),
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
            day=day,
            teacher_name=teachers,
        )

    @staticmethod
    def __extract_time(lesson):
        time = lesson.find("div", class_="lesson-time").text.split('—')
        return time[0].strip(), time[1].strip() if len(time) == 2 else None

    @staticmethod
    def __extract_room(lesson):
        room_div = lesson.find("div", class_="pull-right")
        if room_div.find("a", class_="text-nowrap") is not None:
            return False, room_div.find("a", class_="text-nowrap").text
        return True, None

    @staticmethod
    def __extract_lesson_type(lesson):
        lesson_type = lesson.find("div", class_="label label-default label-lesson")
        change_types = {
            "Пр": "практика",
            "Лек": "лекция",
            "Лаб": "лабораторная работа",
            "Ауд": "аудиторная работа"
        }
        return change_types.get(lesson_type.text) if lesson_type else None

    @staticmethod
    def __extract_weeks(lesson):
        weeks = lesson.find("span", recursive=False)
        class_mapping = {
            "lesson-square-0": 2,
            "lesson-square-1": 1,
            "lesson-square-2": 0
        }
        return class_mapping.get(weeks["class"][1]) if weeks else None

    @staticmethod
    def __extract_teachers(lesson):
        return [
            teacher.find("a").text.replace('\xa0', ' ')
            for teacher in lesson.find_all("span", class_="text-nowrap")
        ]

    def __extract_dates(self, lesson):
        if dates := lesson.find("span", class_="lesson-dates"):
            date_start, date_end = self.__parse_date_range(dates.text)
            return date_start, date_end
        return None, None

    @staticmethod
    def __extract_lesson_info(lesson):
        if lesson.find("div", class_="label label-gray") is not None:
            lesson.find("div", class_="label label-gray").extract()
        if lesson.find("div", class_="label label-pink") is not None:
            lesson.find("div", class_="label label-pink").extract()

        text = '#'.join(lesson.strings).replace("\n", "").replace(",", "").split('#')
        text = [item for item in text if item.strip() != '']

        subgroup = None

        if text[1] in ['Лек', 'Лаб', 'Ауд', 'Пр']:
            lesson_name = text[2]
            if len(text) > 3 and '\xa0' not in text[3]:
                subgroup = text[3]
        else:
            lesson_name = text[1]
            if len(text) > 3 and '\xa0' not in text[2]:
                subgroup = text[2]

        return lesson_name, subgroup

    @staticmethod
    def __parse_date_range(date_range):
        dates = date_range.replace(', ', '—').replace('\n(', '').replace(')\n', '').split('—')
        date_start = dates[0].strip()
        date_end = dates[1].strip() if len(dates) > 1 else None
        return date_start, date_end

    async def __set_info_to_db(self, lessons: List[List[LessonExtracting]]):
        for lessons_group in lessons:
            for lesson in lessons_group:
                self.db.hset(name=f"lessons:{self._index}", key="lesson", value=lesson.model_dump_redis())
                self._index += 1
