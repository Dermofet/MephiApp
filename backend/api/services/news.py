from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.news import NewsRepository
from backend.schemas.news import NewsOutputSchema, NewsSchema


class NewsService:
    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> NewsOutputSchema:
        news = await NewsRepository.get_by_id(db, guid)
        if news is None:
            raise HTTPException(404, "Новость не найдена")
        return NewsOutputSchema(**NewsSchema.from_orm(news).dict())

    @staticmethod
    async def get_all(db: AsyncSession, tag: str, offset: int, limit: int = 100) -> dict[str, list[NewsOutputSchema]]:
        news = await NewsRepository.get_all(db, tag, offset, limit)
        return {"news": [NewsOutputSchema(**NewsSchema.from_orm(_).dict()) for _ in news]}

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await NewsRepository.delete(db, guid)
