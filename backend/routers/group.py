from api.backend.config import config
from api.backend.database.connection import get_session
from api.backend.schemas.group import GroupCreateSchema, GroupOutputSchema
from api.backend.services.group import GroupService
from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.post(
    "/groups",
    response_model=GroupOutputSchema,
    response_description="Группа успешно создано",
    status_code=status.HTTP_201_CREATED,
    description="Создать группу и вернуть его",
    summary="Создание группы",
)
async def create(
        schemas: GroupCreateSchema,
        db: AsyncSession = Depends(get_session),
        group_service: GroupService = Depends(),
):
    return await group_service.create(db=db, schemas=schemas)


@router.get(
    "/groups",
    response_model=dict[str, list[str]],
    status_code=status.HTTP_200_OK,
    description="Получить все группы",
    summary="Получить все группы",
)
async def get_all(
        db: AsyncSession = Depends(get_session),
        group_service: GroupService = Depends()
):
    return await group_service.get_all(db)


@router.get(
    "/groups/{name}",
    response_model=GroupOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Получить группу по названию",
    summary="Получить группу по названию",
)
async def get(
        name: str,
        db: AsyncSession = Depends(get_session),
        group_service: GroupService = Depends(),
):
    return await group_service.get_by_name(db, name=name)
