import datetime
import json
import os

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.news import NewsModel
from backend.database.models.news_image import NewsImageModel


async def bulk_insert_news(db: AsyncSession) -> None:
    try:
        print(f'News inserting')
        news_buffer = []
        news_image_buffer = []
        with open(f'{os.getcwd()}/parsing/news/news.json', 'r', encoding='utf-8') as fp:
            dict_json = json.loads(fp.read().replace("'", '\''))
            for news_record in dict_json:
                news_image_models = []
                for news_img in news_record["news_imgs"]:
                    buf_news_img = NewsImageModel(
                        url=news_img["img"],
                        text=news_img["text"]
                    )
                    if buf_news_img in news_image_buffer:
                        news_image_models.append(news_image_buffer.intersection(buf_news_img).pop())
                    else:
                        news_image_models.append(buf_news_img)

                news_buffer.append(NewsModel(
                    news_id=news_record["id"],
                    text=news_record["news_text"],
                    imgs=news_image_models,
                    title=news_record["preview_text"],
                    preview_url=news_record["preview_img"],
                    date=datetime.datetime.strptime(news_record["date"], "%d.%m.%Y").date(),
                    tag=news_record["tag"]))

                if len(news_buffer) % 5000 == 0:
                    print(f'Inserting {len(news_buffer)} items')
                    async with db.begin():
                        db.add_all(news_buffer)
                        await db.commit()
                        print('Committed changes')
                    news_buffer.clear()
                    news_image_buffer.clear()

        if news_buffer:
            print(f'Inserting {len(news_buffer)} items')
            async with db.begin():
                db.add_all(news_buffer)
                await db.commit()
                print('Committed changes')

    except FileNotFoundError:
        print(f'File {os.getcwd()}/parsing/news/news.json was not found.')
    except sqlalchemy.exc.IntegrityError as e:
        print(f'Error: {str(e)}')
        await db.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        await db.rollback()
