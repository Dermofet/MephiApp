from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.config import config
from backend.database.connection import get_session_yield
from backend.schemas.academic import AcademicCreateSchema, AcademicOutputSchema
from backend.services.academic import AcademicService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.post(
    "/academics",
    response_model=AcademicOutputSchema,
    response_description="Ученое звание успешно создано",
    status_code=status.HTTP_201_CREATED,
    description="Создать ученое звание и вернуть его",
    summary="Создание ученого звания",
)
async def create(
        schemas: AcademicCreateSchema,
        db: AsyncSession = Depends(get_session_yield),
        academic_service: AcademicService = Depends(),
):
    return await academic_service.create(db=db, schemas=schemas)