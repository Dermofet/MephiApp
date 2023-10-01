import asyncio
import sys

from celery_worker import tasks
from config import config


# def event_loop():
#     try:
#         loop = asyncio.get_event_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#     yield loop

#     if not loop.is_closed:
#         loop.close()

def schedule():
    tasks.parse_schedule.delay()


def start_semester():
    tasks.parse_start_semester.delay()


def all_news():
    tasks.etl_all_news.delay()


def new_news():
    tasks.parse_new_news.delay()


args = [arg for arg in sys.argv if arg != ""]

# Проверить, что был передан хотя бы один аргумент
if len(args) < 2:
    msg = "Usage: python etl_.py [parameter]\n" + \
          "Available parameters:\n" + \
          "  - schedule         Parse and load schedule\n" + \
          "  - start_semester   Parse and load start semester\n" + \
          "  - all_news         Parse and load all news\n" + \
          "  - new_news         Parse and load new news"
    print(msg)
else:
    # Получить значение параметра
    parameter = args[1]
    if parameter == "all_news":
        all_news()
    elif parameter == "new_news":
        new_news()
    elif parameter == "schedule":
        schedule()
    elif parameter == "start_semester":
        start_semester()
    else:
        print(f"Unknown parameter: {parameter}")
