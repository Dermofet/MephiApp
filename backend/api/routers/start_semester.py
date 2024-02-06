from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.api.database.connection import get_session
from backend.api.routers.utils import get_version
from backend.api.schemas.start_semester import StartSemesterOutputSchema
from backend.api.services.utils import get_start_semester_service
from utils.version import Version

router = APIRouter(prefix="/api")


@router.get(
    "/v2.0/start_semester",
    response_model=StartSemesterOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Получить дату начала семестра",
    summary="Получить дату",
)
@router.get(
    "/start_semester",
    response_model=StartSemesterOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Получить дату начала семестра",
    summary="Получить дату",
)
async def get(
    version: Version = Depends(get_version),
    session: AsyncSession = Depends(get_session),
):
    start_semester_service = await get_start_semester_service(version, session)
    return await start_semester_service.get()
