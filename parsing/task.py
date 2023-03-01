import json
import time
from dataclasses import dataclass
from typing import Optional

import aiohttp
import bs4


@dataclass
class PostTask:
    tid: int
    str_json: str
    url: str
    description: str

    async def perform(self):
        async with aiohttp.ClientSession() as session:
            t = time.time()
            async with session.post(self.url,
                                    data=self.str_json,
                                    headers={"Content-Type": "application/json"}) as resp:
                answer = await resp.text()
                print(f'Task: {self.tid}; execution time: {time.time() - t}\n'
                      f'Description: {self.description}\n'
                      f'Status: {resp.status}\n'
                      f'RequestJson: {self.str_json}\n'
                      f'ResponseJSON: {answer}')
                print()
                if resp.status == 201 or resp.status == 409 or resp.status == 400:
                    return True
        return False

    def __repr__(self):
        print(f'Tid: {self.tid}\n'
              f'Description: {self.description}')


@dataclass
class PutTask:
    tid: int
    str_json: str
    url: str
    description: str

    async def perform(self):
        async with aiohttp.ClientSession() as session:
            t = time.time()
            async with session.put(self.url,
                                   data=self.str_json,
                                   headers={"Content-Type": "application/json"}) as resp:

                print(f'Task: {self.tid}; execution time: {time.time() - t}\n'
                      f'Description: {self.description}\n'
                      f'Status: {resp.status}')
                if resp.status == 200:
                    print()
                    return True
                if resp.status == 404:
                    print(self.str_json)
                    print()
                    dict_json = json.loads(self.str_json)
                    name = dict_json["name"].split('.')
                    if len(name) == 3:
                        dict_json["name"] = name[0] + "."
                        self.str_json = json.dumps(dict_json, ensure_ascii=False, indent=3)
                    elif len(name) == 2:
                        return True

        return False

    def __repr__(self):
        return f'Tid: {self.tid}\n' \
               f'Description: {self.description}'
