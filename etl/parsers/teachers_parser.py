import asyncio
import json
from os import name
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
            auth_url: str,
            auth_service_url: str,
            login: str,
            password: str,
            single_connection_client: bool = True,
            is_logged: bool = True,
    ):
        super().__init__(
            redis_host=redis_host, 
            redis_port=redis_port, 
            db=db,
            auth_url=auth_url,
            auth_service_url=auth_service_url,
            login=login,
            password=password, 
            single_connection_client=single_connection_client, 
            is_logged=is_logged,
        )
        self.url = url

    async def parse(self):
        self.logger.info("Start parsing teachers")

        await self.parse_teachers_fullname()

        self.logger.info("Teachers were parsed successfully")

    async def parse_teachers_fullname(self):
        categories = await self.get_categories()
        teachers = await self.get_teachers(categories)
        self.set_info_to_db(teachers)

    async def get_categories(self):
        soup = await self.soup_with_auth(self.url)
        
        if soup.find("ul", class_="pagination") is None:
            return []
        
        return [
            self.base_url(self.url) + item.find("a")['href']
            for item in soup.find("ul", class_="pagination").findAll("li")
        ]

    async def get_teachers(self, categories_urls: List[HttpUrl]):
        tasks = []
        tasks.extend(
            self.get_teachers_fullname_from_category(category_url)
            for category_url in categories_urls
        )
        
        self.logger.debug(f"Total teachers: {len(tasks)}")
        results = await asyncio.gather(*tasks)

        res = []
        for item in results:
            res.extend(item)
        return res

    async def get_teachers_fullname_from_category(self, category_url: HttpUrl):
        soup = await self.soup_with_auth(category_url)
        res = []
        for item in soup.findAll("a", class_="list-group-item"):
            name_parts = item.text.split()
            name = f"{name_parts[0]} {'.'.join([i[0] for i in name_parts[1:]])}."
            res.append(TeacherFullnameLoading(url=None, alt_url=None, fullname=item.text, name=name, lang="ru"))
        return res

    def set_info_to_db(self, teachers: List[TeacherFullnameLoading]):
        for teacher in teachers:
            self.db.hset(f"teachers:{hash(teacher)}", key="teacher", value=teacher.model_dump_redis())
