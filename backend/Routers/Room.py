from fastapi import APIRouter, Depends, Path
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.Config.config import get_config
from backend.DataBase.connection import get_session
from backend.Filters.Room import RoomFilter
from backend.Services.Room import RoomService

config = get_config()
router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/room/empty",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
    description="Получить все аудитории, в которых не проводятся занятия в заданный период времени",
    summary="Получить пустые аудитории",
)
async def get_empty(
        room_filter: RoomFilter = FilterDepends(RoomFilter),
        db: AsyncSession = Depends(get_session),
        room_service: RoomService = Depends()
):
    return await room_service.get_empty(db, room_filter)
