import asyncio
import json
from typing import List

import bs4
from pydantic import HttpUrl

from etl.parsers.base_parser import BaseParser
from etl.schemas.teacher import TeacherFullnameLoading


class TeachersParser(BaseParser):
    url: HttpUrl

    def __init__(
            self,
            url: HttpUrl,
            redis_host: str,
            redis_port: int,
            db: int,
            single_connection_client: bool = True,
            is_logged: bool = True,
    ):
        super().__init__(redis_host, redis_port, db, single_connection_client, is_logged)
        self.url = url

    async def parse(self):
        await self.parse_teachers_fullname()

    async def parse_teachers_fullname(self):
        categories = await self.get_categories()
        teachers = await self.get_teachers(categories)
        self.set_info_to_db(teachers)

    async def get_categories(self):
        soup = await self.soup(self.url)
        return [
            self.base_url(self.url) + item.find("a")['href']
            for item in soup.find("ul", class_="pagination").findAll("li")
        ]

    async def get_teachers(self, categories_urls: HttpUrl):
        tasks = [
            self.get_teachers_fullname_from_category(category_url)
            for category_url in categories_urls
        ]
        results = await asyncio.gather(*tasks)
        return [TeacherFullnameLoading(**item) for item in results]

    async def get_teachers_fullname_from_category(self, category_url: HttpUrl):
        soup = await self.soup(category_url)
        return [TeacherFullnameLoading(fullname=item.text, lang="ru") for item in soup.findAll("a", class_="list-group-item")]

    def set_info_to_db(self, teachers: List[TeacherFullnameLoading]):
        for teacher in teachers:
            self.db.hset("teachers", hash(teacher), teacher.model_dump())
