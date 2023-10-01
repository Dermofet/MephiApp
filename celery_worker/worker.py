import sys

from celery import Celery
from celery.schedules import crontab

from config import config

sys.path.append("..")

app = Celery(
    config.CELERY_NAME,
    broker=config.RABBITMQ_URI.unicode_string(),
    backend=config.REDIS_URI.unicode_string(),
    include=[
        'celery_worker.tasks',
        'etl.parsers.news_parser',
    ]
)

app.conf.beat_schedule = {
    'parse_schedule_task': {
        'task': 'celery_worker.tasks.parse_schedule',
        'schedule': crontab(minute='0', hour='3', day_of_week='0'),
    },
    'parse_news_task': {
        'task': 'celery_worker.tasks.parse_new_news',
        'schedule': crontab(minute='30'),
    },
    'parse_start_semester_task_09': {
        'task': 'celery_worker.tasks.etl_start_semester',
        'schedule': crontab(day_of_month=1, month_of_year=9),
    },
    'parse_start_semester_task_02': {
        'task': 'celery_worker.tasks.etl_start_semester',
        'schedule': crontab(day_of_month=8, month_of_year=2),
    },
}
app.conf.task_ignore_result = True