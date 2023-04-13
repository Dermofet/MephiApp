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
            self.toFile(obj=res, filename=f'{os.getcwd()}/parsing/news/news.json', mode='w', encoding='utf-8',
                        indent=3, ensure_ascii=False)

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
        news_data["preview_img"] = news[1] if news[1] != "" else None
        news_data.update(news[0])
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
            preview_url = ""
            for i, field in enumerate(text.findAll("p", class_="rtecenter")):
                if field.find("img") is not None:
                    preview_url = field.find("img")['src'] if "https" in field.find("img")['src'] \
                        else self.config.MEPHI_URL + field.find("img")['src']
                    if len(text.findAll("p", class_="rtecenter")) > i + 1:
                        if text.findAll("p", class_="rtecenter")[i+1].find("img") is None:
                            text.findAll("p", class_="rtecenter")[i+1].extract()
                    field.extract()

            imgs = soup.find("div", class_="region region-content").find("div", id="block-views-modern-gallery-block")
            if imgs is not None:
                content = soup.new_tag("div", class_="content")
                content.append(text)
                content.append(imgs.find("div", class_="view-content"))
                text = content
                # for img in soup.find("div", class_="region region-content") \
                #         .find("div", id="block-views-modern-gallery-block").findAll("img"):
                #     result["news_imgs"].append(
                #         {
                #             "img": img['src'] if "https" in img['src'] else self.config.MEPHI_URL + img['src'],
                #             "text": ""
                #         }
                #     )

            result = {
                "id": url.split("news/")[1],
                "news_text": text.prettify() if text is not None else "",
                "news_imgs": []
            }

            return [result, preview_url]
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
                                    found_in_db = True

                await db.close()
                print(f"Total news {len(tasks)}")
                news = await asyncio.gather(*tasks)
                print("Parsing completed")

                self.smartAddData(news, filename=f'{os.getcwd()}/parsing/news/news.json', encoding='utf-8')

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
    def toFile(obj: object, filename: str, encoding: str, indent: int, ensure_ascii: bool, mode: str = "w"):
        try:
            with open(filename, mode=mode, encoding=encoding) as fp:
                json.dump(obj, fp, ensure_ascii=ensure_ascii, indent=indent, default=str)
            print("Data set to file")
        except Exception as e:
            print(e)

    @staticmethod
    def fromFile(filename: str, encoding: str, mode: str = "r"):
        try:
            with open(filename, mode=mode, encoding=encoding) as fp:
                res = json.load(fp)
            print("Data get from file")
            return res
        except Exception as e:
            print(e)

    @staticmethod
    def smartAddData(new_data, filename: str, encoding: str, indent: int = 3):
        tmp_filename = filename + '.tmp'

        with open(tmp_filename, 'w', encoding=encoding) as tmp_file:
            json.dump(new_data, tmp_file, ensure_ascii=False)

        with open(tmp_filename, 'r+', encoding=encoding) as tmp_file:
            tmp_file.seek(0, os.SEEK_END)
            tmp_file.seek(tmp_file.tell() - 1, os.SEEK_SET)
            tmp_file.truncate()
            tmp_file.write(',')

        with open(filename, 'r+', encoding=encoding) as original_file, \
                open(tmp_filename, 'r', encoding=encoding) as tmp_file:

            with open(filename + '.new', 'w', encoding=encoding) as new_file:
                for line in tmp_file:
                    new_file.write(line)

                next(original_file)
                for line in original_file:
                    new_file.write(line)

        os.rename(filename + '.new', filename)

    # @staticmethod
    # def smartAddData(new_data, filename: str, encoding: str, indent: int = 3):
    #     tmp_filename = filename + '.tmp'
    #
    #     with open(filename, 'r', encoding=encoding) as f:
    #         with open(tmp_filename, 'w', encoding=encoding) as tmp_file:
    #             line = f.readline()
    #             if line.strip() == '[':
    #                 tmp_file.write(line)
    #                 tmp_file.write('\n')
    #                 json.dump(new_data, tmp_file, ensure_ascii=False, indent=indent)
    #                 tmp_file.write('\n')
    #             else:
    #                 raise ValueError("File doesn't contain a JSON array")
    #
    #             line = f.readline()
    #             while line.strip() != ']':
    #                 tmp_file.write(line)
    #                 line = f.readline()
    #
    #             tmp_file.write(',\n')
    #             json.dump(new_data, tmp_file, ensure_ascii=False, indent=indent)
    #             tmp_file.write('\n')
    #             tmp_file.write(line)
    #
    #     os.rename(tmp_filename, filename)
