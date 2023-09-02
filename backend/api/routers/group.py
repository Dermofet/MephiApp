from fastapi import APIRouter, Depends
from starlette import status

from backend.api.schemas.group import GroupCreateSchema, GroupOutputSchema
from backend.api.services.group import GroupService
from config import config

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
        group_service: GroupService = Depends(GroupService.get_service),
):
    return await group_service.create(schemas=schemas)


@router.get(
    "/groups",
    response_model=dict[str, list[str]],
    status_code=status.HTTP_200_OK,
    description="Получить все группы",
    summary="Получить все группы",
)
async def get_all(
        group_service: GroupService = Depends(GroupService.get_service),
):
    return await group_service.get_all()


@router.get(
    "/groups/{name}",
    response_model=GroupOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Получить группу по названию",
    summary="Получить группу по названию",
)
async def get(
        name: str,
        group_service: GroupService = Depends(GroupService.get_service),
):
    return await group_service.get_by_name(name=name)
