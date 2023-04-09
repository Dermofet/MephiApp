import asyncio
import json
import os
import sys

import aiohttp
import bs4

from parsing import config


class TeachersFullnameParser:
    def __init__(self):
        self.config = config

    async def parse_teachers_fullname(self):
        async with aiohttp.ClientSession() as session:
            categories = await self.get_categories(session)
            teachers_fullname = await self.get_teachers_fullname(session, categories)
            self.setTeachersFullname(f"{os.getcwd()}/parsing/schedule/teachers/TeachersFullname.json",
                                     obj=teachers_fullname,
                                     mode='w', encoding='utf-8', indent=3, ensure_ascii=False)

    async def get_categories(self, session):
        async with session.get(self.config.MEPHI_TEACHERS_URL) as resp:
            html = await resp.text()
            soup = bs4.BeautifulSoup(html, "lxml")
            categories = []
            for item in soup.find("ul", class_="pagination").findAll("li"):
                categories.append(self.config.HOME_MEPHI_URL + item.find("a")['href'])
            return categories

    async def get_teachers_fullname(self, session, categories):
        res = {"teachers_fullname": []}
        tasks = []
        for category in categories:
            tasks.append(self.get_teachers_fullname_from_category(session, category))
        results = await asyncio.gather(*tasks)
        for result in results:
            res["teachers_fullname"].extend(result)
        return res

    @staticmethod
    async def get_teachers_fullname_from_category(session, category):
        async with session.get(category) as resp:
            html = await resp.text()
            soup = bs4.BeautifulSoup(html, "lxml")
            res = []
            for item in soup.findAll("a", class_="list-group-item"):
                res.append(item.text)
            return res

    @staticmethod
    def setTeachersFullname(filename, obj, mode, encoding, indent, ensure_ascii):
        print(f"Total teachers: {len(obj['teachers_fullname'])}")
        with open(filename, mode=mode, encoding=encoding) as fp:
            json.dump(obj, fp=fp, ensure_ascii=ensure_ascii, indent=indent)
