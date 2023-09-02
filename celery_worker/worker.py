from celery import Celery
from celery.schedules import crontab

from config import config

celery = Celery(
    config.CELERY_NAME,
    broker=config.RABBITMQ_URI.unicode_string(),
)

celery.conf.beat_schedule = {
    'parse_schedule_task': {
        'task': 'etl.celery_task.etl_schedule',
        'schedule': crontab(minute='0', hour='3', day_of_week='0'),
    },
    'parse_news_task': {
        'task': 'etl.celery_task.etl_new_news',
        'schedule': crontab(minute='30'),
    },
    'parse_start_semester_task_09': {
        'task': 'etl.celery_task.etl_schedule',
        'schedule': crontab(day_of_month=1, month_of_year=9),
    },
    'parse_start_semester_task_02': {
        'task': 'etl.celery_task.etl_schedule',
        'schedule': crontab(day_of_month=8, month_of_year=2),
    },
}
