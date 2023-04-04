from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.config import config
from backend.database.connection import get_session_yield
from backend.schemas.preview import PreviewOutputSchema
from backend.services.preview import PreviewService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/previews",
    response_model=dict[str, list[PreviewOutputSchema]],
    status_code=status.HTTP_200_OK,
    description="Получить превью новостей",
    summary="Получить превью новостей",
)
async def get_all(
        tag: str,
        offset: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_session_yield),
        preview_service: PreviewService = Depends()
):
    return await preview_service.get_all(db, tag, offset, limit)


@router.get(
    "/previews/{guid}",
    response_model=PreviewOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Получить превью по id",
    summary="Получить превью по id",
)
async def get(
        guid: UUID4,
        db: AsyncSession = Depends(get_session_yield),
        preview_service: PreviewService = Depends()
):
    return await preview_service.get(db, guid)
