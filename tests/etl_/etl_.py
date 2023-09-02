import asyncio

from etl import celery_tasks


def schedule():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(celery_tasks.etl_schedule())
    finally:
        pass
    loop.close()


def start_semester():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(celery_tasks.etl_start_semester())
    finally:
        loop.close()


def all_news():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(celery_tasks.etl_all_news())
    finally:
        loop.close()


def new_news():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(celery_tasks.etl_new_news())
    finally:
        loop.close()


if __name__ == '__main__':
    # schedule()
    # start_semester()
    all_news()
    # new_news()