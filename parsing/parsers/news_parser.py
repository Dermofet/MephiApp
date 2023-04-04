import asyncio
import datetime
import json
import os
import time
from copy import deepcopy

import bs4
from aiohttp import ClientSession

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
        async with ClientSession() as session:
            tags = await self.parse_tags(session, self.config.MEPHI_NEWS_PAGE_URL)
            tasks = []
            for tag in tags:
                page_count = await self.parse_count_pages(session,
                                                          f'{self.config.MEPHI_NEWS_PAGE_URL}?category={tag["value"]}')
                print(f"Tag '{tag['name']}' contains {page_count} pages")
                for i in range(page_count):
                    tasks.append(self.parse_news_page(session,
                                                      url=f'{self.config.MEPHI_NEWS_PAGE_URL}?category={tag["value"]}&page={i}',
                                                      tag=tag['name']))
            print(f"Total pages {len(tasks)}")
            news = await asyncio.gather(*tasks)
            print("Parsing completed")

            res = []
            for n in news:
                print(n)
                res += n
            self.toFile(obj=res, filename=f'{os.getcwd()}\\news\\news.json', mode='w', encoding='utf-8', indent=3,
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

                news = await self.parse_news(session, news_url)
                news_data.update(news)

                result.append(news_data)
                self.count += 1
                print(self.count)
            return result

        except (Exception,) as e:
            print(e)

    async def parse_news(self, session: ClientSession, url: str):
        try:
            html = await self.get_html(session, url)
            soup = bs4.BeautifulSoup(html, "lxml")

            result = {
                "id": url.split("news/")[1],
                "news_text": "",
                "news_imgs": []
            }

            for field in soup.findAll("p"):
                if field.find("img") is not None:
                    result["news_imgs"].append(
                        {
                            "img": self.config.MEPHI_URL + field.find("img")['src'],
                            "text": field.text.replace(' ', ' ') if field.text != ' ' else ""
                        }
                    )

                if field.text == " ":
                    continue

                if field.has_attr('class') and "rtecenter" in field['class'] and field.find("img") is not None:
                    result["news_imgs"][-1]["text"] = field.text.replace(' ', ' ') if field.text != ' ' else ""
                else:
                    result["news_text"] += field.text.replace(' ', ' ') + "\n"

            return result
        except Exception as err:
            print(err)
            print(url)
            print()

    @staticmethod
    def toFile(obj: object, filename: str, mode: str, encoding: str, indent: int, ensure_ascii: bool):
        try:
            with open(filename, mode=mode, encoding=encoding) as fp:
                json.dump(obj, fp, ensure_ascii=ensure_ascii, indent=indent, default=str)
            print("Data set to file")
        except Exception as e:
            print(e)
