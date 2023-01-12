from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.Config.config import get_config
from backend.DataBase.connection import get_session
from backend.Services.Group import GroupService

config = get_config()
router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/groups",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
    description="Получить все группы",
    summary="Получить все группы",
)
async def get_all(
        db: AsyncSession = Depends(get_session),
        group_service: GroupService = Depends()
):
    return await group_service.get_all(db)
