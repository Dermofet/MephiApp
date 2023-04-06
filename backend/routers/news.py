from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.config import config
from backend.database.connection import get_session_yield
from backend.schemas.news import NewsOutputSchema, NewsSchema
from backend.services.news import NewsService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.get(
    "/news",
    response_model=dict[str, list[NewsOutputSchema]],
    status_code=status.HTTP_200_OK,
    description="Получить новости",
    summary="Получить новости",
)
async def get_all(
        tag: str = "Главные новости",
        offset: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_session_yield),
        news_service: NewsService = Depends()
):
    return await news_service.get_all(db, tag, offset, limit)


@router.get(
    "/news/{guid}",
    response_model=NewsOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Получить группу по названию",
    summary="Получить группу по названию",
)
async def get(
        guid: UUID4,
        db: AsyncSession = Depends(get_session_yield),
        news_service: NewsService = Depends()
):
    return await news_service.get(db, guid)
