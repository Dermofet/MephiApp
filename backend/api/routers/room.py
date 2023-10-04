import datetime
from typing import Annotated, List, Union

from fastapi import APIRouter, Depends, Query
from starlette import status

from backend.api.filters.room import RoomFilter
from backend.api.schemas.room import RoomCreateSchema, RoomOutputSchema
from backend.api.services.room import RoomService
from config import config

router = APIRouter(prefix=config.BACKEND_PREFIX)


# @router.post(
#     "/rooms",
#     response_model=RoomOutputSchema,
#     response_description="Аудитория успешно создано",
#     status_code=status.HTTP_201_CREATED,
#     description="Создать аудитории и вернуть его",
#     summary="Создание аудитории",
# )
# async def create(
#         schemas: RoomCreateSchema,
#         room_service: RoomService = Depends(RoomService.get_service)
# ):
#     return await room_service.create(schemas=schemas)


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
    room_service: RoomService = Depends(RoomService.get_service)
):
    room_filter = RoomFilter(time_start=time_start, time_end=time_end, date_=date_)
    return await room_service.get_empty(room_filter, corps)


@router.get(
    "/rooms",
    response_model=List[str],
    status_code=status.HTTP_200_OK,
    description="Получить все аудитории",
    summary="Получить все аудитории",
)
async def get_all(
    room_service: RoomService = Depends(RoomService.get_service)
):
    return await room_service.get_all()