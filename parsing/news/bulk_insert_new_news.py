import datetime
import json
import os

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.news import NewsModel
from backend.database.models.news_image import NewsImageModel


async def bulk_insert_new_news(db: AsyncSession) -> None:
    try:
        async with db.begin():
            print(f'News inserting')
            news = set()
            news_image = set()
            with open(f'{os.getcwd()}/parsing/news/new_news.json', 'r', encoding='utf-8') as fp:
                dict_json = json.loads(fp.read().replace("'", '\''))
                for news_record in dict_json:
                    news_image_models = []
                    for news_img in news_record["news_imgs"]:
                        buf_news_img = NewsImageModel(
                            url=news_img["img"],
                            text=news_img["text"]
                        )
                        if buf_news_img in news_image:
                            news_image_models.append(news_image.intersection(buf_news_img).pop())
                        else:
                            news_image_models.append(buf_news_img)

                    news.add(NewsModel(
                        news_id=news_record["id"],
                        text=news_record["news_text"],
                        imgs=news_image_models,
                        title=news_record["preview_text"],
                        preview_url=news_record["preview_img"],
                        date=datetime.datetime.strptime(news_record["date"], "%d.%m.%Y").date(),
                        tag=news_record["tag"]))

            print(f'Inserting {len(news)} items')
            db.add_all(news)
            await db.commit()
            print('Committed changes')
            os.remove(f'{os.getcwd()}/parsing/news/new_news.json')
    except FileNotFoundError:
        print(f'File {os.getcwd()}/parsing/news/news.json was not found.')
    # except sqlalchemy.exc.IntegrityError as e:
    #     print(f'Error: {str(e)}')
    #     await db.rollback()
    # except Exception as e:
    #     print(f'Error: {str(e)}')
    #     await db.rollback()
