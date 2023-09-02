from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from backend.config import config
from backend.database.connection import init_db
from backend.routers.academic import router as academic_router
from backend.routers.corps import router as corps_router
from backend.routers.group import router as group_router
from backend.routers.lesson import router as lesson_router
from backend.routers.news import router as news_router
from backend.routers.room import router as room_router
from backend.routers.start_semester import router as start_semester_router
from backend.routers.teacher import router as teacher_router

tags_metadata = [
    {"name": "group", "description": "Работа с группами"},
    {"name": "lesson", "description": "Работа с расписанием"},
    {"name": "room", "description": "Работа с аудиториями"},
    {"name": "teacher", "description": "Работа с преподавателями"},
    {"name": "academic", "description": "Работа с учеными званиями"},
    {"name": "corps", "description": "Работа с корпусами"},
    {"name": "news", "description": "Работа с новостями"},
    {"name": "start_semester", "description": "Работа с датой начала семестра"},
]
app = FastAPI(
    debug=config.DEBUG,
    openapi_tags=tags_metadata,
    openapi_url=f"{config.BACKEND_PREFIX}/openapi.json",
    title=config.BACKEND_TITLE,
    description=config.BACKEND_DESCRIPTION,
)


@app.on_event("startup")
async def init_models():
    await init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(lesson_router, tags=["lesson"])
app.include_router(room_router, tags=["room"])
app.include_router(group_router, tags=["group"])
app.include_router(teacher_router, tags=["teacher"])
app.include_router(academic_router, tags=["academic"])
app.include_router(corps_router, tags=["corps"])
app.include_router(news_router, tags=["news"])
app.include_router(start_semester_router, tags=["start_semester"])
