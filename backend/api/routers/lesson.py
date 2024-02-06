from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.api.database.connection import get_session
from backend.api.routers.utils import get_version
from backend.api.services.utils import get_lesson_service
from utils.version import Version

router = APIRouter(prefix="/api")


@router.get(
    "/v2.0/lessons/groups/{group}",
    response_model=dict,
    response_description="Успешный возврат занятий",
    status_code=status.HTTP_200_OK,
    description="Получить список занятий определенной группы",
    summary="Получение занятий по группе",
)
@router.get(
    "/lessons/groups/{group}",
    response_model=dict,
    response_description="Успешный возврат занятий",
    status_code=status.HTTP_200_OK,
    description="Получить список занятий определенной группы",
    summary="Получение занятий по группе",
)
async def get_by_group(
    group: str,
    lang: str = "ru",
    version: Version = Depends(get_version),
    session: AsyncSession = Depends(get_session),
):
    lesson_service = await get_lesson_service(version, session)
    return await lesson_service.get_by_group(group=group, lang=lang)


@router.get(
    "/v2.0/lessons/teachers/{teacher}",
    response_model=dict,
    response_description="Успешный возврат занятий",
    status_code=status.HTTP_200_OK,
    description="Получить список занятий, где преподает определенный преподаватель",
    summary="Получение занятий по преподавателю",
)
@router.get(
    "/lessons/teachers/{teacher}",
    response_model=dict,
    response_description="Успешный возврат занятий",
    status_code=status.HTTP_200_OK,
    description="Получить список занятий, где преподает определенный преподаватель",
    summary="Получение занятий по преподавателю",
)
async def get_by_teacher(
    teacher: str,
    lang: str = "ru",
    version: Version = Depends(get_version),
    session: AsyncSession = Depends(get_session),
):
    lesson_service = await get_lesson_service(version, session)
    return await lesson_service.get_by_teacher(teacher=teacher, lang=lang)
