import asyncio
from dataclasses import dataclass
from typing import Dict
from urllib.parse import urlparse

import aiohttp
import bs4
from redis import Redis

from logging_ import Logger


@dataclass
class AuthData:
    login: str
    password: str
    tgt: str
    session_id: str


class BaseParser:
    use_auth: bool

    is_logged: bool
    logger: Logger

    to_file: bool
    dirpath: str

    db: Redis

    auth_url: str
    auth_service_url: str

    def __init__(
        self,
        redis: str,
        auth_url: str = None,
        auth_service_url: str = None,
        login: str = None,
        password: str = None,
        use_auth: bool = True,
        single_connection_client: bool = True,
        is_logged: bool = True,
    ):
        self.is_logged = is_logged
        self.db = Redis.from_url(redis, single_connection_client=single_connection_client)
        self.logger = Logger(is_logged)

        self.use_auth = use_auth
        self.auth_url = auth_url
        self.auth_service_url = auth_service_url
        self.auth_data = AuthData(login, password, '', '')

    @staticmethod
    async def session(headers: Dict[str, str] = None, cookies: Dict[str, str] = None) -> aiohttp.ClientSession:
        async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
            yield session

    async def soup(self, url: str) -> bs4.BeautifulSoup:
        async for session in self.session():
            if self.use_auth and self.auth_data.session_id == '':
                await self.__auth(session)

            # proxy = None

            while True:
                async with session.get(
                    url, 
                    cookies={'_session_id': self.auth_data.session_id if self.use_auth else None}, 
                ) as response:
                        
                    if response.status != 200:
                        self.logger.info(f'Error status: {response.status}. Try again...')
                        await asyncio.sleep(1)
                        if self.use_auth:
                            await self.__auth(session)
                    else:
                        html = await response.text()
                        break

        return bs4.BeautifulSoup(html, "lxml")

    @staticmethod
    def base_url(url):
        parsed = urlparse(url)
        return f'{parsed.scheme}://{parsed.netloc}'
    
    async def download_file_with_auth(self, url: str, filepath: str):
        async for session in self.session():
            if self.use_auth and self.auth_data.session_id == '':
                await self.__auth(session)
            
            async with session.get(url, cookies={'_session_id': self.auth_data.session_id}) as response:
                if response.status != 200:
                    await asyncio.sleep(5)
                    if self.use_auth:
                        await self.__auth(session)
                
                with open(filepath, 'wb') as file:
                    file.write(await response.read())
    
    async def __auth(self, session: aiohttp.ClientSession):
        try:
            await self.__get_session_id(session)
        except Exception:
            await self.__get_tgt(session)
            await self.__get_session_id(session)

    @staticmethod
    def __get_cookies_from_response(response):
        cookies = {}
        if cookie_header := response.headers.get('set-cookie'):
            cookie_values = cookie_header.split(';')
            for cookie_value in cookie_values:
                key_value = cookie_value.split('=')
                if len(key_value) == 2:
                    if key_value[0] == ' path':
                        continue

                    key = key_value[0].strip()
                    value = key_value[1].strip()
                    cookies[key] = value
        return cookies

    async def __get_login_data(self, login: str, password: str):
        async for session in self.session():

            # Получение страницы с формой авторизации
            async with session.get(self.auth_url) as response:
                cookies = self.__get_cookies_from_response(response)
                document = bs4.BeautifulSoup(await response.text(), 'lxml')
            
                # Получение токенов для авторизации
                authenticity_token = document.select_one('input[name="authenticity_token"]')['value']
                lt = document.select_one('input[name="lt"]')['value']

                form_data = aiohttp.FormData()
                body_fields = {
                    'utf8': '✓',
                    'authenticity_token': authenticity_token,
                    'lt': lt,
                    'username': login,
                    'password': password,
                    'button': '',
                }
                for key, value in body_fields.items():
                    form_data.add_field(key, value)


                return form_data, cookies

    async def __get_tgt(self, session: aiohttp.ClientSession):
        while True:
            body, cookies = await self.__get_login_data(self.auth_data.login, self.auth_data.password)
            async with session.post(
                    self.auth_url, 
                    data=body,
                    cookies=cookies,
                    allow_redirects=False,
            ) as response:

                if response.status == 503:
                    await asyncio.sleep(5)
                    continue

                if response.status != 303:
                    raise Exception(f'Response status code is {response.status}')

                self.auth_data.tgt = response.headers.getall('set-cookie')[1].split('=')[1].split(';')[0]
                print(f'tgt: {self.auth_data.tgt}')
                break

    async def __get_session_id(self, session: aiohttp.ClientSession):
        async with session.get(
                self.auth_service_url,
                cookies={'tgt': self.auth_data.tgt},
                allow_redirects=False,
        ) as response:

            if response.status != 303:
                raise Exception(f'Cannot get tgt. Response status code is {response.status}')

            redirect_url = bs4.BeautifulSoup(await response.text(), 'lxml').find('a')['href']
        
        async with session.get(redirect_url, allow_redirects=False) as response:
            print(await response.text())

            if response.status != 302:
                raise Exception(f'Cannot get session_id. Response status code is {response.status}')
            
            self.auth_data.session_id = response.headers.get('set-cookie').split('=')[1].split(';')[0]
            print(f'session_id: {self.auth_data.session_id}')

