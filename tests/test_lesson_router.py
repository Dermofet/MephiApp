import pytest
from httpx import AsyncClient

from backend.Config.config import get_config
from backend.main import app
from backend.Schemas.Lesson import LessonCreate, LessonOutput


@pytest.mark.anyio
async def test_lesson_post():
    config = get_config()
    async with AsyncClient(app=app, base_url=f'{config.BACKEND_LOCALHOST}/{config.BACKEND_PREFIX}/') as ac:
        response = await ac.post("lessons", data=LessonCreate(
            **{
                "time_start": "8.30",
                "time_end": "10.15",
                "dot": false,
                "weeks": 0,
                "day": "monday",
                "date_start": None,
                "date_end": None,
                "type": "Лек",
                "name": "Занятие 1",
                "subgroup": None,
                "group": "Группа 1",
                "course": "Курс 1",
                "room": "А-100",
                "academic": "Бакалавриат",
                "teacher_name": "Иванов И.И.",
                "lang": "ru"
            }
        ))
        assert response.status_code == 201
        assert response.json() == {
                "time_start": "8.30",
                "time_end": "10.15",
                "dot": false,
                "weeks": 0,
                "day": "monday",
                "date_start": None,
                "date_end": None,
                "type": "Лек",
                "name": "Занятие 1",
                "subgroup": None,
                "group": "Группа 1",
                "course": "Курс 1",
                "room": "А-100",
                "academic": "Бакалавриат",
                "teacher_name": "Иванов И.И.",
                "lang": "ru"
            }
    async with AsyncClient(app=app, base_url=f'{config.BACKEND_LOCALHOST}/{config.BACKEND_PREFIX}/') as ac:
        response = await ac.post("lessons", data=LessonCreate(
            **{
                "time_start": "8.30",
                "time_end": "10.15",
                "dot": false,
                "weeks": 0,
                "day": "monday",
                "date_start": None,
                "date_end": None,
                "type": "Лек",
                "name": "Занятие 1",
                "subgroup": None,
                "group": "Группа 1",
                "course": "Курс 1",
                "room": "А-100",
                "academic": "Бакалавриат",
                "teacher_name": "Иванов И.И.",
                "lang": "ru"
            }
        ))
        assert response.status_code == 409
        assert response.json() == {
            "time_start": "8.30",
            "time_end": "10.15",
            "dot": false,
            "weeks": 0,
            "day": "monday",
            "date_start": None,
            "date_end": None,
            "type": "Лек",
            "name": "Занятие 1",
            "subgroup": None,
            "group": "Группа 1",
            "course": "Курс 1",
            "room": "А-100",
            "academic": "Бакалавриат",
            "teacher_name": "Иванов И.И.",
            "lang": "ru"
        }


@pytest.mark.anyio
async def test_lesson_get_id():
    config = get_config()
    async with AsyncClient(app=app, base_url=f'{config.BACKEND_LOCALHOST}/{config.BACKEND_PREFIX}/') as ac:
        response = await ac.post("id/", data=LessonCreate(
            **{
                "time_start": "8.30",
                "time_end": "10.15",
                "dot": false,
                "weeks": 0,
                "day": "monday",
                "date_start": None,
                "date_end": None,
                "type": "Лек",
                "name": "Занятие 1",
                "subgroup": None,
                "group": "Группа 1",
                "course": "Курс 1",
                "room": "А-100",
                "academic": "Бакалавриат",
                "teacher_name": "Иванов И.И.",
                "lang": "ru"
            }
        ))
        assert response.status_code == 201
        assert response.json() == {
                "time_start": "8.30",
                "time_end": "10.15",
                "dot": false,
                "weeks": 0,
                "day": "monday",
                "date_start": None,
                "date_end": None,
                "type": "Лек",
                "name": "Занятие 1",
                "subgroup": None,
                "group": "Группа 1",
                "course": "Курс 1",
                "room": "А-100",
                "academic": "Бакалавриат",
                "teacher_name": "Иванов И.И.",
                "lang": "ru"
            }
    async with AsyncClient(app=app, base_url=f'{config.BACKEND_LOCALHOST}/{config.BACKEND_PREFIX}/') as ac:
        response = await ac.post("lessons", data=LessonCreate(
            **{
                "time_start": "8.30",
                "time_end": "10.15",
                "dot": false,
                "weeks": 0,
                "day": "monday",
                "date_start": None,
                "date_end": None,
                "type": "Лек",
                "name": "Занятие 1",
                "subgroup": None,
                "group": "Группа 1",
                "course": "Курс 1",
                "room": "А-100",
                "academic": "Бакалавриат",
                "teacher_name": "Иванов И.И.",
                "lang": "ru"
            }
        ))
        assert response.status_code == 409
        assert response.json() == {
            "time_start": "8.30",
            "time_end": "10.15",
            "dot": false,
            "weeks": 0,
            "day": "monday",
            "date_start": None,
            "date_end": None,
            "type": "Лек",
            "name": "Занятие 1",
            "subgroup": None,
            "group": "Группа 1",
            "course": "Курс 1",
            "room": "А-100",
            "academic": "Бакалавриат",
            "teacher_name": "Иванов И.И.",
            "lang": "ru"
        }

# {
#     "time_start": "8.30",
#     "time_end": "10.15",
#     "dot": false,
#     "weeks": 0,
#     "day": "monday",
#     "date_start": null,
#     "date_end": null,
#     "type": "Лек",
#     "name": "Занятие 1",
#     "subgroup": null,
#     "group": "Группа 1",
#     "course": 1,
#     "room": "А-100",
#     "academic": "Бакалавриат",
#     "teacher_name": "Иванов И.И.",
#     "lang": "ru"
# }