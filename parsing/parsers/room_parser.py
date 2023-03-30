import json
import os.path
import sys

import bs4
import requests

from parsing import config


class RoomParser:
    def __init__(self):
        self.config = config

    def parse_room(self):
        html = requests.get(self.config.MEPHI_ROOM_URL).text
        soup = bs4.BeautifulSoup(html, "lxml")

        res_rooms = []
        res_corps = []
        i = 0

        box = soup.find("div", class_="box")
        for name, rooms in zip(box.findAll("h3", class_="light"), box.findAll("ul", class_="list-inline")):
            i += len(rooms.findAll("a"))
            res_corps.append({
                "name": name.text
            })
            for room in rooms.findAll("a"):
                res_rooms.append({
                    "corps": name.text,
                    "number": room.text
                })
        print(f'Count corps = {len(box.findAll("h3", class_="light"))}')
        print(f"Count rooms = {i}")

        self.setInfoToFile((res_corps, res_rooms), f'{os.getcwd()}\\rooms\\rooms.json', mode='w', encoding='utf-8', indent=3,
                           ensure_ascii=False)

    @staticmethod
    def setInfoToFile(res_lists, filename, mode, encoding, indent, ensure_ascii):
        dict_dump = {
            "corps": res_lists[0],
            "rooms": res_lists[1]
        }
        with open(filename, mode, encoding=encoding) as fp:
            json.dump(dict_dump, fp=fp, indent=indent, ensure_ascii=ensure_ascii)