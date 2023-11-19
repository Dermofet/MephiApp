from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.api.database.connection import get_session
from backend.api.routers.utils import get_version
from backend.api.schemas.teacher import TeacherOutputSchema
from backend.api.services.utils import get_teacher_service
from utils.version import Version

router = APIRouter(prefix="/api/v2.0")


@router.get(
    "/teachers/{lang}",
    response_model=dict[str, list[str]],
    status_code=status.HTTP_200_OK,
    description="Получить полные ФИО всеx преподавателей",
    summary="Получить всех преподавателей",
)
async def get_all(
    lang: str = "ru",
    version: Version = Depends(get_version),
    session: AsyncSession = Depends(get_session),
):
    teacher_service = await get_teacher_service(version, session)
    return await teacher_service.get_all(lang)


@router.get(
    "/teachers/{name}",
    response_model=TeacherOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Получить полное ФИО преподавателя",
    summary="Получить ФИО преподавателя",
)
async def get_by_name(
    name: str,
    lang: str = "ru",
    version: Version = Depends(get_version),
    session: AsyncSession = Depends(get_session),
):
    teacher_service = await get_teacher_service(version, session)
    return await teacher_service.get_by_name(name=name, lang=lang)
