import json
import os
import sys

import bs4
import requests

from parsing import config


class TeachersFullnameParser:
    def __init__(self):
        self.config = config

    def parse_teachers_fullname(self):
        self.setTeachersFullname(f"{os.getcwd()}/teachers/TeachersFullname.json",
                                 obj=self.getTeachersFullname(),
                                 mode='w', encoding='utf-8', indent=3, ensure_ascii=False)

    def getTeachersFullname(self):
        html = requests.get(self.config.MEPHI_TEACHERS_URL).text
        soup = bs4.BeautifulSoup(html, "lxml")
        categories = []
        for item in soup.find("ul", class_="pagination").findAll("li"):
            categories.append(self.config.HOME_MEPHI_URL + item.find("a")['href'])

        res = {"teachers_fullname": []}
        for category in categories:
            html = requests.get(category).text
            soup = bs4.BeautifulSoup(html, "lxml")
            for item in soup.findAll("a", class_="list-group-item"):
                res["teachers_fullname"].append(item.text)
        return res

    @staticmethod
    def setTeachersFullname(filename, obj, mode, encoding, indent, ensure_ascii):
        with open(filename, mode=mode, encoding=encoding) as fp:
            json.dump(obj, fp=fp, ensure_ascii=ensure_ascii, indent=indent)
