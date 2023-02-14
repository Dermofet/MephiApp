from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.config import config
from backend.database.connection import get_session
from backend.schemas.corps import CorpsCreateSchema, CorpsOutputSchema
from backend.services.corps import CorpsService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.post(
    "/corps",
    response_model=CorpsOutputSchema,
    response_description="Корпус успешно создано",
    status_code=status.HTTP_201_CREATED,
    description="Создать корпус и вернуть его",
    summary="Создание корпуса",
)
async def create(
        schemas: CorpsCreateSchema,
        db: AsyncSession = Depends(get_session),
        corps_service: CorpsService = Depends(),
):
    return await corps_service.create(db=db, schemas=schemas)
