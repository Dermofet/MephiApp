from fastapi import APIRouter, Depends
from starlette import status

from backend.api.schemas.corps import CorpsCreateSchema, CorpsOutputSchema
from backend.api.services.corps import CorpsService
from config import config

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
        corps_service: CorpsService = Depends(CorpsService.get_service),
):
    return await corps_service.create(schemas=schemas)


@router.get(
    "/corps",
    response_model=dict[str, list[str]],
    status_code=status.HTTP_200_OK,
    description="Получить корпус",
    summary="Получить корпус",
)
async def get_all(
        corps_service: CorpsService = Depends(CorpsService.get_service),
):
    return await corps_service.get_all()
