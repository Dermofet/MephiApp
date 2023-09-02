import datetime

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.config import config
from backend.database.connection import get_session_yield
from backend.schemas.start_semester import StartSemesterCreateSchema, StartSemesterOutputSchema
from backend.services.start_semester import StartSemesterService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.post(
    "/start_semester",
    response_model=StartSemesterOutputSchema,
    response_description="Дата успешно создана",
    status_code=status.HTTP_201_CREATED,
    description="Создать дату начала семестра и вернуть ее",
    summary="Создание даты",
)
async def create(
        schemas: StartSemesterCreateSchema,
        db: AsyncSession = Depends(get_session_yield),
        start_semester_service: StartSemesterService = Depends()
):
    return await start_semester_service.create(db=db, schemas=schemas)


@router.get(
    "/start_semester",
    response_model=StartSemesterOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Получить дату начала семестра",
    summary="Получить дату",
)
async def get(
        db: AsyncSession = Depends(get_session_yield),
        start_semester_service: StartSemesterService = Depends()
):
    return await start_semester_service.get(db)


@router.put(
    "/start_semester",
    response_model=StartSemesterOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Получить дату начала семестра",
    summary="Получить дату",
)
async def update(
        schema: StartSemesterCreateSchema,
        db: AsyncSession = Depends(get_session_yield),
        start_semester_service: StartSemesterService = Depends()
):
    return await start_semester_service.update(db, schema)
