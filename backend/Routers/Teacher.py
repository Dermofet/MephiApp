from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.Config.config import get_config
from backend.DataBase.connection import get_session
from backend.Services.Teacher import TeacherService

config = get_config()
router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/teachers",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
    description="Получить полные ФИО всеx преподавателей",
    summary="Получить всех преподавателей",
)
async def get_all(
        db: AsyncSession = Depends(get_session),
        teacher_service: TeacherService = Depends()
):
    return await teacher_service.get_all(db)
