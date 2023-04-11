import asyncio
import datetime
import json
import os
import time
from copy import deepcopy

import bs4
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_session_return
from backend.repositories.news import NewsRepository
from backend.schemas.news import NewsSchema
from parsing import config


class NewsParser:
    def __init__(self):
        self.config = config
        self.count = 0

    @staticmethod
    async def get_html(session: ClientSession, url: str):
        async with session.get(url) as resp:
            result = await resp.text()
            return result

    def start_parse_news(self):
        _ = time.time()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.parse_all_news())
        print(f"Total time: {time.time() - _}")

    async def parse_all_news(self):
        async with ClientSession(trust_env=True) as session:
            tags = await self.parse_tags(session, self.config.MEPHI_NEWS_PAGE_URL)
            tasks = []
            for tag in tags:
                page_count = await self.parse_count_pages(session,
                                                          f'{self.config.MEPHI_NEWS_PAGE_URL}?category={tag["value"]}')
                print(f"Tag '{tag['name']}' contains {page_count} pages")
                for i in range(page_count):
                    tasks.append(self.parse_news_page(session,
                                                      url=f'{self.config.MEPHI_NEWS_PAGE_URL}'
                                                          f'?category={tag["value"]}&page={i}',
                                                      tag=tag['name']))
            print(f"Total pages {len(tasks)}")
            news = await asyncio.gather(*tasks)
            print("Parsing completed")

            res = []
            for n in news:
                res += n
            self.toFile(obj=res, filename=f'{os.getcwd()}/parsing/news/news.json', mode='w', encoding='utf-8', indent=3,
                        ensure_ascii=False)

    async def parse_tags(self, session: ClientSession, url: str):
        html = await self.get_html(session, url)
        soup = bs4.BeautifulSoup(html, "lxml")

        tags = []
        for tag in soup.find("select", class_="form-select required").findAll("option"):
            tags.append({
                'name': tag.text,
                'value': tag['value']
            })

        return tags

    async def parse_count_pages(self, session: ClientSession, url: str):
        html = await self.get_html(session, url)
        soup = bs4.BeautifulSoup(html, "lxml")

        href_last_page = soup.find("li", class_="pager-last last").find("a")['href']
        page_count = int(href_last_page.split("page=")[1]) + 1
        return page_count

    async def parse_news_page(self, session: ClientSession, url: str, tag: str):
        try:
            html = await self.get_html(session, url)
            page = bs4.BeautifulSoup(html, "lxml")

            result = []
            for preview in page.find("div", class_="view-content").findAll("div", class_="views-row"):
                try:
                    result.append(await self.parse_full_news(session, preview, tag))
                    self.count += 1
                    print(self.count)
                except Exception as e:
                    print(f"Get an error: {e}")
            return result

        except (Exception,) as e:
            print(e)

    async def parse_full_news(self, session, preview, tag: str):
        news_data, news_url = await self.parse_preview(preview, tag)
        news = await self.parse_news(session, news_url)
        news_data["preview_img"] = news["news_imgs"][0]["img"] if news["news_imgs"] else None
        news_data.update(news)
        return news_data

    async def parse_preview(self, preview, tag: str):
        try:
            preview_fields = preview.select(".field-content")

            if len(preview_fields) == 4:
                news_data = {
                    "preview_img": preview_fields[0].find("img")['src'],
                    "preview_text": preview_fields[3].find("a").text,
                    "date": preview_fields[1].find("span", class_="date-display-single").text,
                    "tag": tag
                }
                news_url = self.config.MEPHI_URL + preview_fields[3].find("a")['href']
            else:
                news_data = {
                    "preview_img": None,
                    "preview_text": preview_fields[2].find("a").text,
                    "date": preview_fields[0].find("span", class_="date-display-single").text,
                    "tag": tag
                }
                news_url = self.config.MEPHI_URL + preview_fields[2].find("a")['href']

            return news_data, news_url
        except Exception as e:
            print(e)

    async def parse_news(self, session: ClientSession, url: str):
        try:
            html = await self.get_html(session, url)
            soup = bs4.BeautifulSoup(html, "lxml")

            text = soup.find("div", class_="field-item even")
            result = {"id": url.split("news/")[1],
                      "news_text": text.prettify() if text is not None else "",
                      "news_imgs": []}

            for img in soup.find("div", class_="region region-content").findAll("img"):
                result["news_imgs"].append(
                    {
                        "img": img['src'] if "https" in img['src'] else self.config.MEPHI_URL + img['src'],
                        "text": img.parent.text.replace(' ', ' ') if img.parent.text != ' ' else ""
                    }
                )
            for field in soup.findAll("p"):
                if field.has_attr('class') and "rtecenter" in field['class'] and field.find("img") is not None:
                    result["news_imgs"][-1]["text"] = field.text.replace(' ', ' ') if field.text != ' ' else ""

            return result
        except Exception as err:
            print(err, url)

    def parse_new_news(self):
        _ = time.time()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.get_new_news())
        print(f"Total time: {time.time() - _}")

    async def get_new_news(self):
        try:
            async with ClientSession(trust_env=True) as session:
                tags = await self.parse_tags(session, self.config.MEPHI_NEWS_PAGE_URL)
                db: AsyncSession = await get_session_return()
                async with db.begin():
                    tasks = []
                    for tag in tags:
                        page_count = await self.parse_count_pages(session, f'{self.config.MEPHI_NEWS_PAGE_URL}'
                                                                           f'?category={tag["value"]}')
                        found_in_db = False
                        for i in range(page_count):
                            if found_in_db:
                                break

                            html = await self.get_html(session, f'{self.config.MEPHI_NEWS_PAGE_URL}'
                                                                f'?category={tag["value"]}&page={i}')
                            soup = bs4.BeautifulSoup(html, "lxml")
                            for preview in soup.find("div", class_="view-content").findAll("div", class_="views-row"):
                                news_id = await self.get_news_id(preview)
                                news = await NewsRepository.get_by_news_id(db, news_id)
                                if not news:
                                    tasks.append(self.parse_full_news(session, preview, tag["name"]))
                                else:
                                    print(NewsSchema.from_orm(news).title)
                                    found_in_db = True

                await db.close()
                print(f"Total pages {len(tasks)}")
                news = await asyncio.gather(*tasks)
                print("Parsing completed")

                self.toFile(obj=news, filename=f'{os.getcwd()}/parsing/news/new_news.json', mode='w', encoding='utf-8',
                            indent=3, ensure_ascii=False)

                old_news = self.fromFile(filename=f'{os.getcwd()}/parsing/news/news.json', mode="r", encoding='utf-8')
                news += old_news
                self.toFile(obj=news, filename=f'{os.getcwd()}/parsing/news/news.json', mode='w', encoding='utf-8',
                            indent=3, ensure_ascii=False)

        except Exception as err:
            print(err)

    async def get_news_id(self, preview):
        preview_fields = preview.select(".field-content")
        if len(preview_fields) == 4:
            news_url = self.config.MEPHI_URL + preview_fields[3].find("a")['href']
        else:
            news_url = self.config.MEPHI_URL + preview_fields[2].find("a")['href']
        return news_url.split("news/")[1]

    @staticmethod
    def toFile(obj: object, filename: str, mode: str, encoding: str, indent: int, ensure_ascii: bool):
        try:
            with open(filename, mode=mode, encoding=encoding) as fp:
                json.dump(obj, fp, ensure_ascii=ensure_ascii, indent=indent, default=str)
            print("Data set to file")
        except Exception as e:
            print(e)

    @staticmethod
    def fromFile(filename: str, mode: str, encoding: str):
        try:
            with open(filename, mode=mode, encoding=encoding) as fp:
                res = json.load(fp)
                return res
        except Exception as e:
            print(e)
