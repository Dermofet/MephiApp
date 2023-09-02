import asyncio
import sys

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


args = []
for arg in sys.argv:
    if arg != "":
        args.append(arg)


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
    if parameter == "schedule":
        schedule()
    elif parameter == "start_semester":
        start_semester()
    elif parameter == "all_news":
        all_news()
    elif parameter == "new_news":
        new_news()
    else:
        print(f"Unknown parameter: {parameter}")
