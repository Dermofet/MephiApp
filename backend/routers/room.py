from api.backend.config import config
from api.backend.database.connection import get_session
from api.backend.filters.room import RoomFilter
from api.backend.schemas.room import RoomCreateSchema, RoomOutputSchema
from api.backend.services.room import RoomService
from fastapi import APIRouter, Depends, Path
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.post(
    "/rooms",
    response_model=RoomOutputSchema,
    response_description="Аудитория успешно создано",
    status_code=status.HTTP_201_CREATED,
    description="Создать аудитории и вернуть его",
    summary="Создание аудитории",
)
async def create(
        schemas: RoomCreateSchema,
        db: AsyncSession = Depends(get_session),
        room_service: RoomService = Depends()
):
    return await room_service.create(db=db, schemas=schemas)


@router.get(
    "/rooms/empty",
    response_model=dict[str, list[dict]],
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
