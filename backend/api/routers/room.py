import datetime
from typing import Annotated, List, Union

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.api.database.connection import get_session
from backend.api.filters.room import RoomFilter
from backend.api.routers.utils import get_version
from backend.api.services.utils import get_room_service
from utils.version import Version

router = APIRouter(prefix="/api/v2.0")


@router.get(
    "/rooms/empty",
    response_model=dict[str, list[dict]],
    status_code=status.HTTP_200_OK,
    description="Получить все аудитории, в которых не проводятся занятия в заданный период времени",
    summary="Получить пустые аудитории",
)
async def get_empty(
    corps: Annotated[Union[list[str], None], Query(description="Корпусы, в которых находятся аудитории")] = None,
    time_start: datetime.time = Query(..., description="Начало отрезка времени, в котором аудитория свободна"),
    time_end: datetime.time = Query(..., description="Конец отрезка времени, в котором аудитория свободна"),
    date_: datetime.date = Query(..., description="Дата, когда аудитория свободна"),
    version: Version = Depends(get_version),
    session: AsyncSession = Depends(get_session),
):
    room_filter = RoomFilter(time_start=time_start, time_end=time_end, date_=date_)
    room_service = await get_room_service(version, session)
    return room_service.get_empty(room_filter, corps)


@router.get(
    "/rooms",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    description="Получить все аудитории",
    summary="Получить все аудитории",
)
async def get_all(
    version: Version = Depends(get_version),
    session: AsyncSession = Depends(get_session),
):
    room_service = await get_room_service(version, session)
    return await room_service.get_all()
