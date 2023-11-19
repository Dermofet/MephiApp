from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.api.database.connection import get_session
from backend.api.routers.utils import get_version
from backend.api.schemas.news import NewsOutputSchema
from backend.api.services.utils import get_news_service
from utils.version import Version

router = APIRouter()


@router.get(
    "/news/all",
    response_model=dict[str, list[NewsOutputSchema]],
    status_code=status.HTTP_200_OK,
    description="Получить новости",
    summary="Получить новости",
)
async def get_all(
    tag: str = "Главные новости",
    offset: int = 0,
    limit: int = 100,
    version: Version = Depends(get_version),
    session: AsyncSession = Depends(get_session),
):
    news_service = await get_news_service(version, session)
    return await news_service.get_all(tag, offset, limit)
