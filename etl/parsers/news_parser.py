import asyncio
from typing import List

from etl.parsers.base_parser import BaseParser
from etl.schemas.news import NewsLoading
from etl.schemas.news_img import NewsImageLoading


class NewsParser(BaseParser):
    url: str
    chunks: int

    def __init__(
            self,
            url: str,
            chunks: int,
            redis_host: str,
            redis_port: int,
            db: int,
            single_connection_client: bool = True,
            is_logged: bool = True,
    ):
        super().__init__(redis_host, redis_port, db, single_connection_client, is_logged)
        self.url = url
        self.chunks = chunks

    def full_url(self, url: str):
        return self.base_url(self.url) + url

    async def parse_all_news(self):
        self.logger.info("Start parsing news")

        tags = await self.parse_tags()
        tasks = []
        for tag in tags:
            page_count = await self.parse_count_pages(f'{self.url}?category={tag["value"]}')

            self.logger.info(f"Tag '{tag['name']}' contains {page_count} pages")

            tasks.extend(
                self.parse_news_page(
                    url=f'{self.url}?category={tag["value"]}&page={i}',
                    tag=tag['name'],
                )
                for i in range(page_count)
            )
        news = await self.execute_tasks(tasks)
        self.set_info_to_db(news)

        self.logger.info("All news parsed and set in the db")

    async def execute_tasks(self, tasks):
        chunks = [tasks[i:i + self.chunks] for i in range(0, len(tasks), self.chunks)]

        res = []
        for i, chunk in enumerate(chunks):
            self.logger.debug(f"Parsing chunk {i + 1} out of {len(chunks)}")
            news = await asyncio.gather(*chunk)
            res.extend(news)

        return res

    async def parse_tags(self):
        soup = await self.soup(self.url)

        return [
            (tag.text, tag['value'])
            for tag in soup.find("select", class_="form-select required").findAll("option")
        ]

    async def parse_count_pages(self, url: str):
        soup = await self.soup(url)

        href_last_page = soup.find("li", class_="pager-last last").find("a")['href']
        return int(href_last_page.split("page=")[1]) + 1

    async def parse_news_page(self, url: str, tag: str):
        try:
            soup = await self.soup(url)

            result = []
            for preview in soup.find("div", class_="view-content").findAll("div", class_="views-row"):
                try:
                    result.append(await self.parse_full_news(preview, tag))
                except Exception as e:
                    self.logger.error(f"Error[parse_news_page]: {e}")
            return result

        except Exception as e:
            self.logger.error(f"Error[parse_news_page]: {e}")

    async def parse_full_news(self, preview, tag: str):
        news_data, news_url = await self.parse_preview(preview, tag)
        news, preview_url = await self.parse_news(news_url)

        if news is None:
            raise TypeError("News is None")

        news_data.preview_img = preview_url if preview_url != "" else None
        news_data.news_id = news["id"]
        news_data.text = news["news_text"]
        news_data.imgs = news["news_imgs"]
        return news_data

    async def parse_preview(self, preview, tag: str):
        try:
            preview_fields = preview.select(".field-content")

            if len(preview_fields) == 4:
                news_data = NewsLoading(
                    preview_url=preview_fields[0].find("img")['src'],
                    title=preview_fields[3].find("a").text,
                    date=preview_fields[1].find("span", class_="date-display-single").text,
                    tag=tag
                )
                news_url = f"{self.base_url(self.url)}{preview_fields[3].find('a')['href']}"
            else:
                news_data = NewsLoading(
                    preview_url=None,
                    title=preview_fields[2].find("a").text,
                    date=preview_fields[0].find("span", class_="date-display-single").text,
                    tag=tag
                )
                news_url = f"{self.base_url(self.url)}{preview_fields[2].find('a')['href']}"
            return news_data, news_url
        except Exception as e:
            self.logger.error(f"Error[parse_preview]: {e}")

    async def is_valid(self, http) -> bool:
        if len(http) > 2083:
            self.logger.debug("Http too long")
            return False
        if "http" not in http or "https" not in http:
            self.logger.debug("Don't contain http or https")
            return False
        return True

    async def parse_news(self, url: str):
        try:
            soup = await self.soup(url)
            result = {
                "id": url.split("news/")[1],
                "news_imgs": []
            }
            preview_url = ""

            text = soup.find("div", class_="field-item even")

            if text:
                self.process_text(result, text, preview_url)
            else:
                self.process_text_without_paragraphs(result, text, preview_url)

            if imgs_block := soup.find("div", class_="region region-content").find(
                "div", id="block-views-modern-gallery-block"
            ):
                self.process_image_block(result, imgs_block, text)

            result["news_text"] = text.prettify() if text else ""

            return result, preview_url

        except Exception as e:
            self.logger.error(f"Error[parse_news]: {e, url}")

    def get_image_source(self, img):
        img_src = img['src']
        if "https" not in img_src:
            img_src = self.full_url(img_src)
        return img_src

    def process_text(self, result, text, preview_url):
        rtecenter_paragraphs = text.findAll("p", class_="rtecenter")
        for i, field in enumerate(rtecenter_paragraphs):
            if img := field.find("img"):
                img_src = self.get_image_source(img)
                if img_src and await self.is_valid(img_src):
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
            preview_url = self.get_image_source(img)
            if preview_url and await self.is_valid(preview_url):
                img.parent.extract()

    def process_text_without_paragraphs(self, result, text, preview_url):
        for img in text.findAll("img"):
            img_src = self.get_image_source(img)
            if img_src and await self.is_valid(img_src):
                if not preview_url:
                    preview_url = img_src
                result["news_imgs"].append({"img": img_src, "text": ""})

    def process_image_block(self, result, imgs_block, text):
        for tag_a in imgs_block.findAll("a"):
            img = tag_a.find("img")
            img['src'] = tag_a['href']
            img_src = self.get_image_source(img)

            if img_src and await self.is_valid(img_src):
                result["news_imgs"].append(
                    NewsImageLoading(url=img_src, text=None)
                )

            for tag in imgs_block.findAll("a"):
                img = tag.find("img")
                img['src'] = tag['href']
                del img['height']
                del img['width']
                tag.insert_before(img)
                tag.extract()

            text.append(imgs_block.find("div", class_="view-content"))

    async def parse_new_news(self):
        self.logger.info("Start parsing new news")
        try:
            tags = await self.parse_tags()

            tasks = []
            for tag in tags:
                tasks.extend(self.get_tasks_from_category(tag["value"]))

            self.set_last_news_id_to_db(tasks[0])

            self.logger.info(f"Total news {len(tasks)}")
            news = await asyncio.gather(*tasks)

            self.set_info_to_db(news)
            self.logger.info("New news parsed")

        except Exception as e:
            self.logger.error(f"Error[parse_new_news]: {e}")

    def get_tasks_from_page(self, last_news_id, soup, tag):
        tasks = []
        for preview in soup.find("div", class_="view-content").findAll("div", class_="views-row"):
            if last_news_id != self.get_news_id(preview):
                tasks.append(self.parse_full_news(preview, tag["name"]))
            else:
                return tasks, True
        return tasks, False

    def get_tasks_from_category(self, tag):
        tasks = []
        page_count = await self.parse_count_pages(f'{self.url}?category={tag}')
        found_in_db = False
        last_news_id = self.get_last_news_id()
        for i in range(page_count):
            if found_in_db:
                break

            soup = await self.soup(f'{self.url}?category={tag}&page={i}')
            new_tasks, found_in_db = self.get_tasks_from_page(last_news_id, soup, tag)
            tasks.extend(new_tasks)
        return tasks

    def get_last_news_id(self) -> str:
        return self.db.get("last_news_id")

    async def get_news_id(self, preview):
        preview_fields = preview.select(".field-content")
        if len(preview_fields) == 4:
            news_url = self.full_url(preview_fields[3].find("a")['href'])
        else:
            news_url = self.full_url(preview_fields[2].find("a")['href'])
        return news_url.split("news/")[1]

    def set_info_to_db(self, news: List[NewsLoading]):
        for item in news:
            self.db.hset("news", item.news_id, item.model_dump())

    def set_last_news_id_to_db(self, news: NewsLoading):
        self.db.set("last_news_id", news.news_id)
