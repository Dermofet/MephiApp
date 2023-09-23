from celery_worker import celery
from config import config
from etl.loaders.news_loader import NewsLoader
from etl.loaders.schedule_loader import ScheduleLoader
from etl.loaders.start_semester_loader import StartSemesterLoader
from etl.parsers.news_parser import NewsParser
from etl.parsers.room_parser import RoomParser
from etl.parsers.schedule_parser import ScheduleParser
from etl.parsers.start_semester_parser import StartSemesterParser
from etl.parsers.teachers_parser import TeachersParser
from etl.transform.schedule_transformer import ScheduleTransformer


@celery.task
async def etl_schedule():
    es = ScheduleParser(
        url=config.MEPHI_SCHEDULE_URL.unicode_string(),
        auth_url=config.MEPHI_AUTH_URL.unicode_string(),
        auth_service_url=config.MEPHI_AUTH_SERVICE_URL.unicode_string(),
        redis_host=config.REDIS_HOST,
        redis_port=config.REDIS_PORT,
        db=config.REDIS_DB,
        login=config.MEPHI_LOGIN,
        password=config.MEPHI_PASSWORD,
        use_auth=False,
    )
    es.db.flushdb()
    await es.parse()
    
    er = RoomParser(
        url=config.MEPHI_ROOM_URL.unicode_string(),
        redis_host=config.REDIS_HOST,
        redis_port=config.REDIS_PORT,
        db=config.REDIS_DB,
        login=config.MEPHI_LOGIN,
        password=config.MEPHI_PASSWORD,
        auth_url=config.MEPHI_AUTH_URL.unicode_string(),
        auth_service_url=config.MEPHI_AUTH_SERVICE_URL.unicode_string(),
        use_auth=False,
    )
    await er.parse()
    
    et = TeachersParser(
        url=config.MEPHI_TEACHERS_URL.unicode_string(),
        redis_host=config.REDIS_HOST,
        redis_port=config.REDIS_PORT,
        db=config.REDIS_DB,
        login=config.MEPHI_LOGIN,
        password=config.MEPHI_PASSWORD,
        auth_url=config.MEPHI_AUTH_URL.unicode_string(),
        auth_service_url=config.MEPHI_AUTH_SERVICE_URL.unicode_string(),
        use_auth=False,
    )
    await et.parse()

    t = ScheduleTransformer(
        redis_host=config.REDIS_HOST,
        redis_port=config.REDIS_PORT,
        db=config.REDIS_DB,
        langs=config.FOREIGN_LANGS
    )
    await t.transform()

    l = ScheduleLoader(
        redis_host=config.REDIS_HOST,
        redis_port=config.REDIS_PORT,
        redis_db=config.REDIS_DB,
        postgres_dsn=config.LOCAL_DB_URI.unicode_string(),
    )
    await l.init_facade()
    await l.load()

@celery.task
async def etl_all_news():
    e = NewsParser(
        url=config.MEPHI_NEWS_PAGE_URL.unicode_string(),
        redis_host=config.REDIS_HOST,
        redis_port=config.REDIS_PORT,
        db=config.REDIS_DB,
        chunks=50,
        use_auth=False,
    )
    await e.parse_all_news()

    l = NewsLoader(
        redis_host=config.REDIS_HOST,
        redis_port=config.REDIS_PORT,
        redis_db=config.REDIS_DB,
        postgres_dsn=config.LOCAL_DB_URI.unicode_string(),
    )
    await l.init_facade()
    await l.load()

@celery.task
async def etl_new_news():
    e = NewsParser(
        url=config.MEPHI_NEWS_PAGE_URL.unicode_string(),
        redis_host=config.REDIS_HOST,
        redis_port=config.REDIS_PORT,
        db=config.REDIS_DB,
        chunks=50,
        use_auth=False,
    )
    await e.parse_new_news()

    l = NewsLoader(
        redis_host=config.REDIS_HOST,
        redis_port=config.REDIS_PORT,
        redis_db=config.REDIS_DB,
        postgres_dsn=config.LOCAL_DB_URI.unicode_string(),
    )
    await l.init_facade()
    await l.load()

@celery.task
async def etl_start_semester():
    e = StartSemesterParser(
        url=config.MEPHI_SCHEDULE_URL.unicode_string(),
        redis_host=config.REDIS_HOST,
        redis_port=config.REDIS_PORT,
        db=config.REDIS_DB,
        login=config.MEPHI_LOGIN,
        password=config.MEPHI_PASSWORD,
        auth_url=config.MEPHI_AUTH_URL.unicode_string(),
        auth_service_url=config.MEPHI_AUTH_SERVICE_URL.unicode_string(),
        use_auth=False,
    )
    await e.parse()

    l = StartSemesterLoader(
        redis_host=config.REDIS_HOST,
        redis_port=config.REDIS_PORT,
        redis_db=config.REDIS_DB,
        postgres_dsn=config.LOCAL_DB_URI.unicode_string(),
    )
    await l.init_facade()
    await l.load()
