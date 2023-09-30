import asyncio
import json
import traceback
from typing import List
from urllib.parse import urlparse
from celery import group

import requests
from bs4 import BeautifulSoup
from redis import Redis

from celery_worker import app
from config import config
from etl.parsers.base_parser import BaseParser
from etl.schemas.news import NewsLoading
from etl.schemas.news_img import NewsImageLoading
from logging_.logger import Logger

# class NewsParser(BaseParser):
#     url: str
#     chunks: int

#     def __init__(
#             self,
#             url: str,
#             chunks: int,
#             redis: str,
#             use_auth: bool,
#             single_connection_client: bool = True,
#             is_logged: bool = True,
#     ):
#         super().__init__(
#             redis=redis,
#             single_connection_client=single_connection_client, 
#             is_logged=is_logged, 
#             use_auth=use_auth
#         )
#         self.url = url
#         self.chunks = chunks

#     async def parse_all_news(self):
#         self.logger.info("Start parsing news")

#         tasks = []
#         for tag in await self.__parse_tags():
#             page_count = await self.__parse_count_pages(f'{self.url}?category={tag[1]}')

#             self.logger.info(f"Tag '{tag[0]}' contains {page_count} pages")

#             tasks.extend(
#                 self.__parse_news_page(
#                     self,
#                     url=f'{self.url}?category={tag[1]}&page={i}',
#                     tag=tag[0],
#                 )
#                 for i in range(page_count)
#             )

#         tasks = await asyncio.gather(*tasks)
#         await self.__execute_tasks(tasks)

#         self.logger.info("All news parsed and set in the db")

#     def full_url(self, url: str):
#         if isinstance(url, str):
#             return self.base_url(self.url) + url
#         return TypeError("url is not str")

#     async def __execute_tasks(self, tasks):
#         chunks = [tasks[i:i + self.chunks] for i in range(0, len(tasks), self.chunks)]

#         res = []
#         for i, chunk in enumerate(chunks):
#             self.logger.debug(f"Parsing chunk {i + 1} out of {len(chunks)}")
#             news = await asyncio.gather(*chunk)
#             res.extend(news)
#             self.__set_info_to_db(news)

#         return res

#     async def __parse_tags(self):
#         soup = await self.soup(self.url)

#         return [
#             (tag.text, tag['value'])
#             for tag in soup.find("select", class_="form-select required").findAll("option")
#         ]

#     async def __parse_count_pages(self, url: str):
#         soup = await self.soup(url)

#         href_last_page = soup.find("li", class_="pager-last last").find("a")['href']
#         return int(href_last_page.split("page=")[1]) + 1

#     @app.task
#     async def __parse_news_page(self, url: str, tag: str):
#         try:
#             soup = await self.soup(url)

#             result = []
#             for preview in soup.find("div", class_="view-content").findAll("div", class_="views-row"):
#                 res = self.__parse_full_news.delay(self, preview, tag)
#                 if res is not None:
#                     result.append(res)
#                 else:
#                     continue

#             self.__set_info_to_db(result)

#         except Exception as e:
#             self.logger.error(f"Error[parse_news_page]:\n{traceback.format_exc()}")

#     @app.task
#     async def __parse_full_news(self, preview, tag: str):
#         try:
#             news_data, news_url = self.__parse_preview(preview, tag)
#             news, preview_url = await self.__parse_news(news_url)

#             if news is None:
#                 raise TypeError("News is None")

#             return NewsLoading(
#                 news_id=news["id"],
#                 title=news_data["title"],
#                 preview_url=preview_url if preview_url != "" else None,
#                 date=news_data["date"],
#                 text=news["news_text"],
#                 tag=tag,
#                 imgs=[
#                     NewsImageLoading(url=img["img"], text=img["text"])
#                     for img in news["news_imgs"]
#                 ],
#             )
#         except Exception as e:
#             self.logger.error(f"Error[parse_full_news]:\n{traceback.format_exc()}")
#             return None

#     def __parse_preview(self, preview, tag: str):
#         try:
#             preview_fields = preview.findAll("div", class_="views-field")

#             if len(preview_fields) == 4:
#                 news_data = {
#                     'preview_url': preview_fields[0].find("img")['src'],
#                     'title': preview_fields[3].find("a").text,
#                     'date': preview_fields[1].find("span", class_="date-display-single").text,
#                     'tag': tag,
#                 }
#                 news_url = f"{self.base_url(self.url)}{preview_fields[3].find('a')['href']}"
#             else:
#                 news_data = {
#                     'preview_url': None,
#                     'title': preview_fields[2].find("a").text,
#                     'date': preview_fields[0].find("span", class_="date-display-single").text,
#                     'tag': tag
#                 }
#                 news_url = f"{self.base_url(self.url)}{preview_fields[2].find('a')['href']}"
#             return news_data, news_url
#         except Exception as e:
#             self.logger.error(f"Error[parse_preview]: {traceback.format_exc()}")

#     def __is_valid(self, http: str) -> bool:
#         if len(http) > 2083:
#             self.logger.debug("Http too long")
#             return False
#         if "http" not in http or "https" not in http:
#             self.logger.debug("Don't contain http or https")
#             return False
#         return True

#     async def __parse_news(self, url: str):
#         try:
#             soup = await self.soup(url)
#             result = {
#                 "id": url.split("news/")[1],
#                 "news_imgs": []
#             }
#             preview_url = ""

#             text = soup.find("div", class_="field-item even")

#             if text:
#                 preview_url = self.__process_text(result, text, preview_url)

#                 if imgs_block := soup.find("div", class_="region region-content").find(
#                     "div", id="block-views-modern-gallery-block"
#                 ):
#                     self.__process_image_block(result, imgs_block, text)

#             result["news_text"] = text.prettify() if text else ""

#             return result, preview_url

#         except Exception as e:
#             self.logger.error(f"Error[parse_news]: {traceback.format_exc(), url}")

#     def __get_image_source(self, img):
#         if "https" not in img:
#             try:
#                 img = self.full_url(img['src'])
#             except Exception as e:
#                 print(f'img: {img}')
#                 self.logger.error(f"Error[get_image_source]: {traceback.format_exc()}")
#         return img if img != '' else None

#     def __process_text(self, result, text, preview_url):
#         rtecenter_paragraphs = text.findAll("p", class_="rtecenter")
#         for i, field in enumerate(rtecenter_paragraphs):
#             if img := field.find("img"):
#                 img_src = self.__get_image_source(img)
#                 if img_src and self.__is_valid(img_src):
#                     if not preview_url:
#                         preview_url = img_src
#                     result["news_imgs"].append({"img": img_src, "text": ""})
#                 else:
#                     field.extract()
#             elif i + 1 < len(rtecenter_paragraphs) and not rtecenter_paragraphs[i + 1].find("img"):
#                 rtecenter_paragraphs[i + 1].extract()
#             field.extract()

#         if not preview_url and text.find("img"):
#             img = text.find("img")
#             preview_url = self.__get_image_source(img)
#             if preview_url and self.__is_valid(preview_url):
#                 img.parent.extract()

#         return preview_url

#     def __process_image_block(self, result, imgs_block, text):
#         for tag_a in imgs_block.findAll("a"):
#             img = tag_a.find("img")
#             if img is not None:
#                 img['src'] = tag_a['href']
#                 img_src = self.__get_image_source(img)

#                 if img_src is not None and self.__is_valid(img_src):
#                     result["news_imgs"].append(
#                         {'img': img_src, 'text': None}
#                     )

#             for tag in imgs_block.findAll("a"):
#                 img = tag.find("img")
#                 img['src'] = tag['href']
#                 del img['height']
#                 del img['width']
#                 tag.insert_before(img)
#                 tag.extract()

#             div_tag = imgs_block.find("div", class_="view-content")
#             if div_tag is not None:
#                 text.append(div_tag)

#     async def parse_new_news(self):
#         self.logger.info("Start parsing new news")
#         try:
#             tags = await self.__parse_tags()

#             tasks = []
#             for tag in tags:
#                 tasks.extend(self.__get_tasks_from_category(tag["value"]))

#             self.__set_last_news_id_to_db(tasks[0])

#             self.logger.info(f"Total news {len(tasks)}")
#             news = await asyncio.gather(*tasks)

#             self.__set_info_to_db(news)
#             self.logger.info("New news parsed")

#         except Exception as e:
#             self.logger.error(f"Error[parse_new_news]: {e}")

#     def __get_tasks_from_page(self, last_news_id, soup, tag):
#         tasks = []
#         for preview in soup.find("div", class_="view-content").findAll("div", class_="views-row"):
#             if last_news_id != self.__get_news_id(preview):
#                 tasks.append(self.__parse_full_news(preview, tag["name"]))
#             else:
#                 return tasks, True
#         return tasks, False

#     async def __get_tasks_from_category(self, tag):
#         tasks = []
#         page_count = await self.__parse_count_pages(f'{self.url}?category={tag}')
#         found_in_db = False
#         last_news_id = self.__get_last_news_id()
#         for i in range(page_count):
#             if found_in_db:
#                 break

#             soup = await self.soup(f'{self.url}?category={tag}&page={i}')
#             new_tasks, found_in_db = self.__get_tasks_from_page(last_news_id, soup, tag)
#             tasks.extend(new_tasks)
#         return tasks

#     def __get_last_news_id(self) -> str:
#         return self.db.get("last_news_id")

#     async def __get_news_id(self, preview):
#         preview_fields = preview.select(".field-content")
#         if len(preview_fields) == 4:
#             news_url = self.full_url(preview_fields[3].find("a")['href'])
#         else:
#             news_url = self.full_url(preview_fields[2].find("a")['href'])
#         return news_url.split("news/")[1]

#     def __set_info_to_db(self, news: List[NewsLoading]):
#         for _ in news:
#             for item in _:
#                 self.db.hset(f"news:{item.news_id}", key="news", value=item.model_dump_redis())

#     def __set_last_news_id_to_db(self, news: NewsLoading):
#         self.db.set("last_news_id", news.news_id)

class NewsParser(BaseParser):
    url: str
    chunks: int

    def __init__(
            self,
            url: str,
            redis: str,
            use_auth: bool,
            single_connection_client: bool = True,
            is_logged: bool = True,
    ):
        super().__init__(
            redis=redis, 
            single_connection_client=single_connection_client, 
            is_logged=is_logged, 
            use_auth=use_auth
        )
        self.url = url

    def create_parse_news_tasks(self, url):
        try:
            logger = Logger()
            logger.info("Start creating tasks")

            for tag in self.parse_tags(url):
                page_count = self.parse_count_pages(f'{url}?category={tag[1]}')
                logger.info(f"Tag '{tag[0]}' contains {page_count} pages")

                tasks = [
                    json.dumps(
                        {
                            "url": f'{url}?category={tag[1]}&page={i}',
                            "tag": tag[0],
                        }
                    ) for i in range(page_count)
                ]
                self.set_data_to_db(self.db, tasks, "news_tasks", "task")

            logger.info("News tasks are created")

        except Exception as e:
            logger.error(f"Error[parse_all_news]: {traceback.format_exc()}")

    @staticmethod
    def base_url(url):
        parsed = urlparse(url)
        return f'{parsed.scheme}://{parsed.netloc}'
    
    @staticmethod
    def get_soup(url):
        with requests.get(url) as response:
            return BeautifulSoup(response.text, 'lxml')

    def parse_tags(self, url: str):
        soup = self.get_soup(url)

        return [
            (tag.text, tag['value'])
            for tag in soup.find("select", class_="form-select required").findAll("option")
        ]

    def parse_count_pages(self, url: str):
        soup = self.get_soup(url)

        href_last_page = soup.find("li", class_="pager-last last").find("a")['href']
        return int(href_last_page.split("page=")[1]) + 1

    @staticmethod
    def parse_news_page_tasks(logger, db, url):
        logger.info("Start parsing news")

        async_results = []
        for key in db.scan_iter("news_tasks:*"):
            async_result = NewsParser.parse_news_page.s(url, **json.loads(db.hget(name=key, key="task")))
            async_results.append(async_result)
            db.delete(key)

        return group(async_results)

    @staticmethod
    @app.task
    def parse_news_page(base_url_str, url, tag):
        try:
            logger = Logger()
            db = Redis(
                host=config.REDIS_HOST, 
                port=config.REDIS_PORT, 
                db=config.REDIS_DB,
                single_connection_client=True
            )

            soup = NewsParser.get_soup(url)

            result = []
            for preview in soup.find("div", class_="view-content").findAll("div", class_="views-row"):
                res = NewsParser.parse_full_news(logger, base_url_str, preview, tag)
                if res is not None:
                    result.append(res)
                if url.split('=')[-1] == '0':
                    NewsParser.__set_last_news_id_to_db(db, tag, res.news_id)

            NewsParser.set_news_to_db(db, result)

        except Exception as e:
            logger.error(f"Error[parse_news_page]: {traceback.format_exc()}")

    @staticmethod
    def parse_full_news(logger, base_url_str, preview, tag: str):
        try:
            news_data, news_url = NewsParser.parse_preview(logger, base_url_str, preview, tag)
            news, preview_url = NewsParser.parse_news(logger, base_url_str, news_url)

            if news is None:
                raise TypeError("News is None")

            return NewsLoading(
                news_id=news["id"],
                title=news_data["title"],
                preview_url=preview_url if preview_url != "" else None,
                date=news_data["date"],
                text=news["news_text"],
                tag=tag,
                imgs=[
                    NewsImageLoading(url=img["img"], text=img["text"])
                    for img in news["news_imgs"]
                ],
            )
        except Exception as e:
            logger.error(f"Error[parse_full_news]:\n{traceback.format_exc()}")
            return None
    
    @staticmethod
    def parse_preview(logger, base_url_str, preview, tag: str):
        try:
            preview_fields = preview.findAll("div", class_="views-field")

            if len(preview_fields) == 4:
                news_data = {
                    'preview_url': preview_fields[0].find("img")['src'],
                    'title': preview_fields[3].find("a").text,
                    'date': preview_fields[1].find("span", class_="date-display-single").text,
                    'tag': tag,
                }
                news_url = f"{NewsParser.base_url(base_url_str)}{preview_fields[3].find('a')['href']}"
            else:
                news_data = {
                    'preview_url': None,
                    'title': preview_fields[2].find("a").text,
                    'date': preview_fields[0].find("span", class_="date-display-single").text,
                    'tag': tag
                }
                news_url = f"{NewsParser.base_url(base_url_str)}{preview_fields[2].find('a')['href']}"
            return news_data, news_url
        except Exception as e:
            logger.error(f"Error[parse_preview]: {traceback.format_exc()}")

    @staticmethod
    def is_valid(logger, http: str) -> bool:
        if len(http) > 2083:
            logger.debug("Http too long")
            return False
        if "http" not in http or "https" not in http:
            logger.debug("Don't contain http or https")
            return False
        return True

    @staticmethod
    def parse_news(logger, base_url_str, url: str):
        try:
            soup = NewsParser.get_soup(url)
                
            result = {
                "id": url.split("news/")[1],
                "news_imgs": []
            }
            preview_url = ""

            text = soup.find("div", class_="field-item even")

            if text:
                preview_url = NewsParser.process_text(logger, base_url_str, result, text, preview_url)

                if imgs_block := soup.find("div", class_="region region-content").find(
                    "div", id="block-views-modern-gallery-block"
                ):
                    NewsParser.process_image_block(logger, base_url_str, result, imgs_block, text)

            result["news_text"] = text.prettify() if text else ""

            return result, preview_url

        except Exception:
            raise Exception(f"Error[parse_news]: {traceback.format_exc(), url}")

    @staticmethod
    def get_image_source(logger, img, base_url_str):
        if "https" not in img:
            try:
                img = NewsParser.base_url(base_url_str) + img['src']
            except Exception as e:
                logger.error(f"Error[get_image_source]: {traceback.format_exc()}")
        return img if img != '' else None

    @staticmethod
    def process_text(logger, base_url_str, result, text, preview_url):
        rtecenter_paragraphs = text.findAll("p", class_="rtecenter")
        for i, field in enumerate(rtecenter_paragraphs):
            if img := field.find("img"):
                img_src = NewsParser.get_image_source(logger, img, base_url_str)
                if img_src and NewsParser.is_valid(logger, img_src):
                    if not preview_url:
                        preview_url = img_src
                    result["news_imgs"].append({"img": img_src, "text": ""})
                else:
                    field.extract()
            elif i + 1 < len(rtecenter_paragraphs) and not rtecenter_paragraphs[i + 1].find("img"):
                rtecenter_paragraphs[i + 1].extract()
            field.extract()

        if not preview_url and text.find("img"):
            img = text.find("img")
            preview_url = NewsParser.get_image_source(logger, img, base_url_str)
            if preview_url and NewsParser.is_valid(logger, preview_url):
                img.parent.extract()

        return preview_url

    @staticmethod
    def process_image_block(logger: Logger, base_url_str, result, imgs_block, text):
        for tag_a in imgs_block.findAll("a"):
            img = tag_a.find("img")
            if img is not None:
                img['src'] = tag_a['href']
                img_src = NewsParser.get_image_source(logger, img, base_url_str)

                if img_src is not None and NewsParser.is_valid(logger, img_src):
                    result["news_imgs"].append(
                        {'img': img_src, 'text': None}
                    )

            for tag in imgs_block.findAll("a"):
                img = tag.find("img")
                img['src'] = tag['href']
                del img['height']
                del img['width']
                tag.insert_before(img)
                tag.extract()

            div_tag = imgs_block.find("div", class_="view-content")
            if div_tag is not None:
                text.append(div_tag)
    
    @staticmethod
    def set_news_to_db(db: Redis, data: List[NewsLoading]):
        for item in data:
            db.hset(f"news:{item.news_id}", key="news", value=item.model_dump_redis())
        print(f"Set {len(data)} items")

    @staticmethod
    def set_data_to_db(db: Redis, data: List[str], pattern_field: str, key_field: str):
        for item in data:
            db.hset(f"{pattern_field}:{hash(item)}", key=key_field, value=item)
            
    async def parse_new_news(self):
        self.logger.info("Start parsing new news")
        try:
            tags = self.parse_tags(self.url)

            tasks = []
            for tag in tags:
                tasks.extend(await self.__get_tasks_from_category(tag))

            self.logger.info(f"Total news {len(tasks)}")
            news = await asyncio.gather(*tasks)

            self.__set_info_to_db(news)
            self.logger.info("New news parsed")

        except Exception as e:
            self.logger.error(f"Error[parse_new_news]: {traceback.format_exc()}")

    def __get_tasks_from_page(self, last_news_id, soup, tag):
        tasks = []

        if soup.find("div", class_="view-content") is None:
            return tasks, False
        
        for preview in soup.find("div", class_="view-content").findAll("div", class_="views-row"):
            if last_news_id != self.__get_news_id(preview):
                tasks.append(self.parse_full_news(self.logger, self.url, preview, tag[0]))
            else:
                return tasks, True
        return tasks, False

    async def __get_tasks_from_category(self, tag):
        tasks = []
        page_count = self.parse_count_pages(f'{self.url}?category={tag[1]}')
        found_in_db = False
        last_news_id = self.__get_last_news_id(tag[0])
        self.logger.info(f"Parsing category {tag[0]}")
        for i in range(page_count):
            if found_in_db:
                self.__set_last_news_id_to_db(tag[0], last_news_id)
                break

            soup = await self.soup(f'{self.url}?category={tag[1]}&page={i}')
            new_tasks, found_in_db = self.__get_tasks_from_page(last_news_id, soup, tag)
            tasks.extend(new_tasks)
        self.logger.info(f"Category {tag[0]} has {len(tasks)} news")
        return tasks

    def __get_last_news_id(self, tag) -> str:
        return self.db.hget("last_news_id", tag)

    def __get_news_id(self, preview):
        preview_fields = preview.select(".field-content")
        if len(preview_fields) == 4:
            news_url = self.base_url(self.url) + preview_fields[3].find("a")['href']
        else:
            news_url = self.base_url(self.url) + preview_fields[2].find("a")['href']
        return news_url.split("news/")[1]

    def __set_info_to_db(self, news: List[NewsLoading]):
        for _ in news:
            for item in _:
                self.db.hset(f"news:{item.news_id}", key="news", value=item.model_dump_redis())

    @staticmethod
    def __set_last_news_id_to_db(db, tag, news_id):
        db.hset("last_news_id", tag, news_id)