import asyncio
import subprocess

from celery import chain

from celery_conf import beat_app
from config import config
from etl.loaders.news_loader import NewsLoader
from etl.loaders.schedule_loader import ScheduleLoader
from etl.loaders.start_semester_loader import StartSemesterLoader
from etl.parsers.new_news_parser import NewNewsParser
from etl.parsers.news_parser import NewsParser
from etl.parsers.room_parser import RoomParser
from etl.parsers.schedule_parser import ScheduleParser
from etl.parsers.start_semester_parser import StartSemesterParser
from etl.parsers.teachers_parser import TeachersParser
from etl.transform.schedule_transformer import ScheduleTransformer
from etl.transform.schedule_translate import ScheduleTranslate


@beat_app.task
def parse_schedule():
    asyncio.run(etl_schedule())

async def etl_schedule():
    es = ScheduleParser(
        lesson_schedule_url=config.MEPHI_SCHEDULE_URL.unicode_string(),
        rooms_schedule_url=config.MEPHI_ROOM_URL.unicode_string(),
        auth_url=config.MEPHI_AUTH_URL.unicode_string(),
        auth_service_url=config.MEPHI_AUTH_SERVICE_URL.unicode_string(),
        redis=config.REDIS_URI.unicode_string(),
        login=config.MEPHI_LOGIN,
        password=config.MEPHI_PASSWORD,
        use_auth=False,
    )
    await es.parse()
    
    er = RoomParser(
        url=config.MEPHI_ROOM_URL.unicode_string(),
        redis=config.REDIS_URI.unicode_string(),
        login=config.MEPHI_LOGIN,
        password=config.MEPHI_PASSWORD,
        auth_url=config.MEPHI_AUTH_URL.unicode_string(),
        auth_service_url=config.MEPHI_AUTH_SERVICE_URL.unicode_string(),
        use_auth=False,
    )
    await er.parse()
    
    et = TeachersParser(
        url=config.MEPHI_TEACHERS_URL.unicode_string(),
        redis=config.REDIS_URI.unicode_string(),
        login=config.MEPHI_LOGIN,
        password=config.MEPHI_PASSWORD,
        auth_url=config.MEPHI_AUTH_URL.unicode_string(),
        auth_service_url=config.MEPHI_AUTH_SERVICE_URL.unicode_string(),
        use_auth=False,
    )
    await et.parse()

    t = ScheduleTransformer(
        redis=config.REDIS_URI.unicode_string(),
        langs=config.FOREIGN_LANGS,
        iam_token=config.IAM_TOKEN,
        folder_id=config.FOLDER_ID,
    )
    await t.transform()

    l = ScheduleLoader(
        redis=config.REDIS_URI.unicode_string(),
        postgres_dsn=config.DB_URI.unicode_string(),
    )
    l.init_facade()
    await l.load()


@beat_app.task
def translate_schedule():        
    asyncio.run(etl_translate_schedule())

async def etl_translate_schedule():
    # result = subprocess.run(['bash', "yandex_auth.sh"], capture_output=True, text=True)
    # output = result.stdout
    # return_code = result.returncode

    # if return_code == 0:
    #     print(f"Скрипт успешно выполнен. Вывод: {output}")
    # else:
    #     print(f"Ошибка при выполнении скрипта. Код завершения: {return_code}, Вывод: {output}")
    #     raise Exception

    t = ScheduleTranslate(
        langs=config.FOREIGN_LANGS,
        iam_token=config.IAM_TOKEN,
        folder_id=config.FOLDER_ID,
        redis=config.REDIS_URI.unicode_string(),
        postgres_dsn=config.DB_URI.unicode_string(),
    )
    t.init_facade()
    await t.translate()

@beat_app.task
def etl_all_news():
    e = NewsParser(
        url=config.MEPHI_NEWS_PAGE_URL.unicode_string(),
        redis=config.REDIS_URI.unicode_string(),
        use_auth=False,
    )

    e.create_parse_news_tasks(config.MEPHI_NEWS_PAGE_URL.unicode_string())
    chain(e.parse_news_page_tasks(e.logger, e.db, e.url), load_news.si()).delay()

@beat_app.task
def load_news():
    l = NewsLoader(
        redis=config.REDIS_URI.unicode_string(),
        postgres_dsn=config.DB_URI.unicode_string(),
    )
    l.logger.debug("Loading news")
    l.init_facade()
    asyncio.run(l.load())


@beat_app.task
def parse_new_news():
    asyncio.run(etl_new_news())

async def etl_new_news():
    e = NewNewsParser(
        url=config.MEPHI_NEWS_PAGE_URL.unicode_string(),
        redis=config.REDIS_URI.unicode_string(),
        postgres_dsn=config.DB_URI.unicode_string(),
        use_auth=False,
    )
    await e.parse_new_news()

    l = NewsLoader(
        redis=config.REDIS_URI.unicode_string(),
        postgres_dsn=config.DB_URI.unicode_string(),
    )
    l.init_facade()
    await l.load()

    await asyncio.sleep(1)


@beat_app.task
def parse_start_semester():
    asyncio.run(etl_start_semester())

async def etl_start_semester():
    e = StartSemesterParser(
        url=config.MEPHI_SCHEDULE_URL.unicode_string(),
        redis=config.REDIS_URI.unicode_string(),
        use_auth=False,
    )
    await e.parse()

    l = StartSemesterLoader(
        redis=config.REDIS_URI.unicode_string(),
        postgres_dsn=config.DB_URI.unicode_string(),
    )
    l.init_facade()
    await l.load()
