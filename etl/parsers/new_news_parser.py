import asyncio
import traceback
from typing import List

from etl.loaders.base_loader import BaseLoader, WrapperBaseLoader
from etl.parsers.news_parser import NewsParser
from etl.schemas.news import NewsLoading

class NewNewsParser(WrapperBaseLoader, NewsParser):
    def __init__(
        self,
        url: str,
        redis: str,
        postgres_dsn: str,
        auth_url: str = None, 
        auth_service_url: str = None, 
        login: str = None, 
        password: str = None, 
        use_auth: bool = True, 
        single_connection_client: bool = True,
        debug: bool = False,
        is_logged: bool = True
    ):
        super().__init__(
            url=url,
            redis=redis, 
            auth_url=auth_url, 
            auth_service_url=auth_service_url,
            login=login, 
            password=password,
            use_auth=use_auth,
            single_connection_client=single_connection_client,
            is_logged=is_logged,
            debug=debug,
            postgres_dsn=postgres_dsn
        )

    async def parse_new_news(self):
        self.logger.info("Start parsing new news")
        try:
            tags = self.parse_tags(self.url)

            news = []
            for tag in tags:
                news.extend(await self.__get_tasks_from_category(tag))

            self.logger.info(f"Total news {len(news)}")

            self.__set_info_to_db(news)
            self.logger.info("New news parsed")

        except Exception as e:
            self.logger.error(f"Error[parse_new_news]: {traceback.format_exc()}")

    async def __get_tasks_from_page(self, soup, tag):
        news = []

        if soup.find("div", class_="view-content") is None:
            return news, False
        
        for preview in soup.find("div", class_="view-content").findAll("div", class_="views-row"):
            if await self.loader.facade_db.get_by_news_id_news(self.__get_news_id(preview)) is None:
                news.append(self.parse_full_news(self.logger, self.url, preview, tag[0]))
            else:
                return news, True
        return news, False

    async def __get_tasks_from_category(self, tag):
        news = []
        page_count = self.parse_count_pages(f'{self.url}?category={tag[1]}')
        found_in_db = False
        self.logger.info(f"Parsing category {tag[0]}")
        for i in range(page_count):
            if found_in_db:
                break

            soup = await self.soup(f'{self.url}?category={tag[1]}&page={i}')
            news_, found_in_db = await self.__get_tasks_from_page(soup, tag)
            news.extend(news_)

        self.logger.info(f"Category {tag[0]} has {len(news)} news")
        return news

    def __get_news_id(self, preview):
        preview_fields = preview.select(".field-content")
        if len(preview_fields) == 4:
            news_url = self.full_url(self.url, preview_fields[3].find("a")['href'])
        else:
            news_url = self.full_url(self.url, preview_fields[2].find("a")['href'])
        return news_url.split("news/")[1]

    def __set_info_to_db(self, news: List[NewsLoading]):
        for item in news:
            self.db.hset(f"news:{item.news_id}", key="news", value=item.model_dump_redis())
