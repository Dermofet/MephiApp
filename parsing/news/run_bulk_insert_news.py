import asyncio
import sys
import time
import traceback

sys.path.append("/api")

from bulk_insert_news import bulk_insert_news

from backend.database.connection import get_session_return
from parsing import config


async def set_news():
    db = await get_session_return()
    await bulk_insert_news(db)
    await db.close()


if __name__ == '__main__':
    _ = time.time()

    loop = asyncio.get_event_loop()

    try:
        print("--SET INFO--: News")
        loop.run_until_complete(set_news())
        print("Completed: News")
        print()
    except Exception as err:
        print(f"Error: {err}")
        loop.stop()
    finally:
        loop.close()

    print(f'Time: {time.time() - _}')
