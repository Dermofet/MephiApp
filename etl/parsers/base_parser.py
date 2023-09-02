from dataclasses import dataclass
from typing import Dict
from urllib.parse import urlparse, quote, urlencode

import aiohttp
import bs4
from redis import Redis

from logging_ import Logger


@dataclass
class AuthData:
    login: str
    password: str
    headers: Dict[str, str]
    cookies: Dict[str, str]
    body: str


class BaseParser:
    is_logged: bool
    logger: Logger

    to_file: bool
    dirpath: str

    db: Redis

    auth_url: str

    def __init__(
        self,
        redis_host: str,
        redis_port: int,
        db: int,
        auth_url: str = None,
        login: str = None,
        password: str = None,
        single_connection_client: bool = True,
        is_logged: bool = True,
    ):
        self.is_logged = is_logged
        self.db = Redis(host=redis_host, port=redis_port, db=db, single_connection_client=single_connection_client)
        self.logger = Logger(is_logged)

        self.auth_url = auth_url
        if self.auth_url is None:
            self.auth_data = None
        else:
            self.auth_data = AuthData(login, password, {}, {}, "")

    @staticmethod
    async def session(headers: Dict[str, str] = None, cookies: Dict[str, str] = None) -> aiohttp.ClientSession:
        # filtered_cookies = None
        # if cookies is not None:
        #     filtered_cookies = {k: v for k, v in cookies.items() if k.lower() != 'path'}
        # async with aiohttp.ClientSession(headers=headers, cookies=filtered_cookies) as session:
        async with aiohttp.ClientSession() as session:
            yield session

    async def soup(self, url: str) -> bs4.BeautifulSoup:
        async for session in self.session():
            async with session.get(url) as response:
                html = await response.text()
        return bs4.BeautifulSoup(html, "lxml")

    @staticmethod
    def base_url(url):
        parsed = urlparse(url)
        return f'{parsed.scheme}://{parsed.netloc}'
    
    async def login(self):
        self.auth_data = await self.__get_login_data(self.auth_data.login, self.auth_data.password)

    async def soup_with_auth(self, url: str) -> bs4.BeautifulSoup:
        async for session in self.session(self.auth_data.headers, self.auth_data.cookies):
            tgt = await self.__auth(session)
            print(tgt)
            self.auth_data.cookies['tgt'] = tgt
            print(self.auth_data.cookies)

        async for session in self.session(headers=self.auth_data.headers, cookies=self.auth_data.cookies):
            async with session.get(url) as response:
                html = await response.text()
                
        return bs4.BeautifulSoup(html, "lxml")

    @staticmethod
    def __get_cookies_from_response(response):
        cookies = {}
        cookie_header = response.headers.get('set-cookie')
        if cookie_header:
            cookie_values = cookie_header.split(';')
            for cookie_value in cookie_values:
                key_value = cookie_value.split('=')
                if len(key_value) == 2:
                    key = key_value[0].strip()
                    value = key_value[1].strip()
                    cookies[key] = value
        return cookies

    @staticmethod
    def __get_cookie_header(cookies):
        cookie_list = [f'{key}={value}' for key, value in cookies.items()]
        return '; '.join(cookie_list)

    async def __get_login_data(self, login, password):
        async for session in self.session():

            # Получение страницы с формой авторизации
            async with session.get(self.auth_url) as response:
                cookies = self.__get_cookies_from_response(response)
                document = bs4.BeautifulSoup(await response.text(), 'lxml')
            
                # Получение токенов для авторизации
                authenticity_token = document.select_one('input[name="authenticity_token"]')['value']
                lt = document.select_one('input[name="lt"]')['value']

                body_fields = {
                    'utf8': '✓',
                    'authenticity_token': authenticity_token,
                    'lt': lt,
                    'username': login,
                    'password': password,
                    'button': '',
                }

                # Вычисление длины тела запроса
                body = '&'.join([f'{key}={value}' for key, value in body_fields.items()])
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Content-Length': str(len(body)),
                }

                return AuthData(login, password, headers, cookies, body)

    async def __auth(self, session: aiohttp.ClientSession):
        cookies = self.auth_data.cookies
        # cookies.pop('path')
        self.auth_data.headers["Cookie"] = self.__get_cookie_header(cookies)
        body = urlencode(self.auth_data.body)
        # print(f'Cookies: {cookies}')
        print(f'Header: {self.auth_data.headers}')
        print(f'Body: {body}')
        async with session.post(
            self.auth_url, 
            data=body, 
            headers=self.auth_data.headers
        ) as response:
            print(await response.text())

            # Проверка на успешную авторизацию
            if response.status == 303:
                set_cookie_header = response.headers.get('set-cookie')
                tgt_index = set_cookie_header.index('tgt=')
                session_id_index = set_cookie_header.index(',_mephi_casino_session=')
                return set_cookie_header[tgt_index:session_id_index]

            if response.status == 200:
                raise Exception('Your session is expired. Authorize again')
            else:
                raise Exception(f'Response status code is {response.status}')

