from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.api.database.connection import get_session
from backend.api.routers.utils import get_version
from backend.api.schemas.group import GroupOutputSchema
from backend.api.services.utils import get_group_service
from utils.version import Version

router = APIRouter(prefix="/api")


@router.get(
    "/v2.0/groups",
    response_model=dict[str, list[str]],
    status_code=status.HTTP_200_OK,
    description="Получить все группы",
    summary="Получить все группы",
)
@router.get(
    "/groups",
    response_model=dict[str, list[str]],
    status_code=status.HTTP_200_OK,
    description="Получить все группы",
    summary="Получить все группы",
)
async def get_all(
    version: Version = Depends(get_version),
    session: AsyncSession = Depends(get_session),
):
    group_service = await get_group_service(version, session)
    return await group_service.get_all()


@router.get(
    "/v2.0/groups/{name}",
    response_model=GroupOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Получить группу по названию",
    summary="Получить группу по названию",
)
@router.get(
    "/groups/{name}",
    response_model=GroupOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Получить группу по названию",
    summary="Получить группу по названию",
)
async def get(
    name: str,
    version: Version = Depends(get_version),
    session: AsyncSession = Depends(get_session),
):
    group_service = await get_group_service(version, session)
    return await group_service.get_by_name(name=name)
