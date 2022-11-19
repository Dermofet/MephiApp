class Settings:
    URL_ALL_SCHEDULE = "https://home.mephi.ru/study_groups/"
    URL_TEACHERS_SCHEDULE = "https://home.mephi.ru/tutors"
    URL_HOME_MEPHI = "https://home.mephi.ru"
    NEWS_URL = "https://mephi.ru/press/news"
    HOST_URL = "https://mephi.ru"
    NEWS_CAT_URLS = {
        "main": NEWS_URL + "?category=1387",
        "region": NEWS_URL + "?category=1412",
        "sp_cul": NEWS_URL + "?category=1389",
        "workday": NEWS_URL + "?category=1810",
    }
    TEACHERS_FULLNAME_PATH = "FastAPI_SQLAlchemy/parsing/schedule/TeachersFullname.json"
    PREVIEW_DIR = "FastAPI_SQLAlchemy/parsing/preview/"
    NEWS_DIR = "FastAPI_SQLAlchemy/parsing/news/"
    BUFFER_1 = 'buffer_1'
    BUFFER_2 = 'buffer_2'


settings = Settings()
