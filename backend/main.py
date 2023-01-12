from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from backend.Config.config import get_config
from backend.DataBase.connection import init_db
from backend.Routers.Group import router as group_router
from backend.Routers.Lesson import router as lesson_router
from backend.Routers.Room import router as room_router
from backend.Routers.Teacher import router as teacher_router

tags_metadata = [
    {"name": "group", "description": "Работа с группами"},
    {"name": "lesson", "description": "Работа с расписанием"},
    {"name": "room", "description": "Работа с аудиториями"},
    {"name": "teacher", "description": "Работа с преподавателями"},
]
config = get_config()
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
