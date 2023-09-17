from fastapi import APIRouter, Depends
from pydantic import UUID4
from starlette import status

from backend.api.schemas.news import NewsOutputSchema
from backend.api.services.news import NewsService
from config import config

router = APIRouter(prefix=config.BACKEND_PREFIX)


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
        news_service: NewsService = Depends(NewsService.get_service),
):
    return await news_service.get_all(tag, offset, limit)

# TODO Удалить

# @router.get(
#     "/news/{guid}",
#     response_model=NewsOutputSchema,
#     status_code=status.HTTP_200_OK,
#     description="Получить группу по названию",
#     summary="Получить группу по названию",
# )
# async def get(
#         guid: UUID4,
#         news_service: NewsService = Depends(NewsService.get_service),
# ):
#     return await news_service.get(guid)
