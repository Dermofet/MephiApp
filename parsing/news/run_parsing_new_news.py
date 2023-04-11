import asyncio
import sys

sys.path.append("/api")

from backend.database.connection import get_session_return
from parsing.news.bulk_insert_new_news import bulk_insert_new_news
from parsing.parsers.news_parser import NewsParser


async def set_news():
    db = await get_session_return()
    await bulk_insert_new_news(db)
    await db.close()


if __name__ == '__main__':
    news_parser = NewsParser()
    news_parser.parse_new_news()

    loop = asyncio.get_event_loop()

    try:
        print()
        print("--SET INFO--: News")
        loop.run_until_complete(set_news())
        print("Completed: News")
        print()
    except Exception as err:
        print(f"Error: {err}")
        loop.stop()
    finally:
        loop.close()
        