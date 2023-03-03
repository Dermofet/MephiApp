import json
import time
import uuid
from dataclasses import dataclass
from typing import Optional

import aiohttp
import bs4
from async_google_trans_new import AsyncTranslator

translator = AsyncTranslator()


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


@dataclass
class TranslatePutTask:
    tid: int
    data: dict
    getId_url: str
    url: str
    description: str
    lang: str
    src_lang: str

    async def perform(self):
        async with aiohttp.ClientSession() as session:
            t = time.time()
            self.data['lang'] = self.src_lang
            async with session.get(self.getId_url,
                                   data=json.dumps(self.data, ensure_ascii=False),
                                   headers={"Content-Type": "application/json"}
                                   ) as resp1:
                guid = await resp1.text()
                try:
                    guid = uuid.UUID(guid.replace('"', '').replace("-", ""))

                    self.data['lang'] = self.lang
                    if self.data['type'] is not None:
                        self.data['type'] = await translator.translate(self.data['type'], lang_tgt=self.lang, lang_src=self.src_lang)
                    self.data['name'] = await translator.translate(self.data['name'], lang_tgt=self.lang, lang_src=self.src_lang)
                    if self.data['subgroup'] is not None:
                        self.data['subgroup'] = await translator.translate(self.data['subgroup'], lang_tgt=self.lang,
                                                                           lang_src=self.src_lang)

                    self.data = json.dumps(self.data, ensure_ascii=False)

                    async with session.put(f'{self.url}/{guid}',
                                           data=self.data,
                                           headers={"Content-Type": "application/json"}) as resp2:
                        print(f'Task: {self.tid}; execution time: {time.time() - t}\n'
                              f'Description: {self.description}\n'
                              f'Status: {resp2.status}\n'
                              f'RequestJson: {self.data}\n'
                              f'ResponseJSON: {await resp2.text()}')
                        print()
                        if resp2.status == 201 or resp2.status == 409:
                            return True
                except ValueError as err:
                    print(guid)
        return False

    def __repr__(self):
        print(f'Tid: {self.tid}\n'
              f'Description: {self.description}')
