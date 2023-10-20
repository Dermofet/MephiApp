from typing import List

from pydantic import UUID4
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.database.models.news import NewsModel
from backend.api.database.models.news_image import NewsImageModel
from backend.api.schemas.news import NewsCreateSchema


class NewsDAO:
    """
    DAO для работы с новостями
    """

    _session: AsyncSession

    def __init__(self, session: AsyncSession):
        self._session = session

    """
    Создание новости
    """

    async def get_by_id(self, guid: UUID4) -> NewsModel:
        news = await self._session.execute(select(NewsModel).where(NewsModel.guid == guid).limit(1))
        return news.scalar()

    """
    Получение всех новостей по id новости
    """

    async def get_by_news_id(self, news_id: str) -> NewsModel:
        news = await self._session.execute(select(NewsModel).where(NewsModel.news_id == news_id).limit(1))
        return news.scalar()

    async def get_images(self, news: NewsModel) -> List[NewsImageModel]:
        images = await self._session.execute(select(NewsImageModel).where(NewsImageModel.news_guid == news.guid))
        return images.scalars().unique().all()

    """
    Получение всех новостей
    """

    async def get_all(self, tag: str, offset: int, limit: int = 100) -> List[NewsModel]:
        news = await self._session.execute(
            select(NewsModel).where(NewsModel.tag == tag).order_by(desc(NewsModel.date)).offset(offset).limit(limit)
        )
        return news.scalars().unique().all()

    """
    Обновление новости
    """

    async def bulk_insert(self, data: List[NewsCreateSchema]) -> None:
        insert_data = []
        for news in data:
            imgs = [NewsImageModel(url=img.url, text=img.text) for img in news.imgs]
            insert_data.append(
                NewsModel(
                    news_id=news.news_id,
                    title=news.title,
                    preview_url=news.preview_url,
                    date=news.date,
                    text=news.text,
                    tag=news.tag,
                    imgs=imgs,
                )
            )
        self._session.add_all(insert_data)
        await self._session.flush()

    """
    Удаление новости
    """

    async def delete(self, guid: UUID4) -> None:
        await self._session.execute(delete(NewsModel).where(NewsModel.guid == guid))
        await self._session.flush()
