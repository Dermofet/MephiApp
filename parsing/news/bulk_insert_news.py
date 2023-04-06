import datetime
import json
import os

from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.news import NewsModel
from backend.database.models.news_image import NewsImageModel
from backend.database.models.preview import PreviewModel


async def bulk_insert_news(db: AsyncSession) -> None:
    try:
        async with db.begin():
            print(f'News inserting')
            news = set()
            news_image = set()
            preview = set()
            with open(f'{os.getcwd()}/parsing/news/news.json', 'r', encoding='utf-8') as fp:
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
                            print("NewsImageModel exists")
                        else:
                            news_image_models.append(buf_news_img)

                    preview_model = PreviewModel(
                        url=news_record["preview_img"],
                        text=news_record["preview_text"],
                        date=datetime.datetime.strptime(news_record["date"], "%d.%m.%Y").date(),
                        tag=news_record["tag"]
                    )
                    if preview_model in preview:
                        preview_model = preview.intersection(preview_model).pop()
                        print("PreviewModel exists")
                    else:
                        preview.add(preview_model)

                    news.add(NewsModel(
                        news_id=news_record["id"],
                        news_text=news_record["news_text"],
                        news_imgs=news_image_models,
                        preview=preview_model))

            print(f'Inserting {len(news)} items')
            db.add_all(news)
            await db.commit()
            print('Committed changes')
    except FileNotFoundError:
        print(f'File {os.getcwd()}/news.json was not found.')
    except sqlalchemy.exc.IntegrityError as e:
        print(f'Error: {str(e)}')
        await db.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        await db.rollback()
