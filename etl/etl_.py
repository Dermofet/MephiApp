import sys

from celery_conf import beat_tasks


def schedule():
    beat_tasks.parse_schedule.delay()


def start_semester():
    beat_tasks.parse_start_semester.delay()


def all_news():
    beat_tasks.etl_all_news.delay()


def new_news():
    beat_tasks.parse_new_news.delay()

def translate_schedule():
    beat_tasks.translate_schedule.delay()


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
    elif parameter == "translate_schedule":
        translate_schedule()
    else:
        print(f"Unknown parameter: {parameter}")
