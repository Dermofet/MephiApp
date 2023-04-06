from typing import List

from pydantic import UUID4
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.news import NewsModel
from backend.database.models.news_image import NewsImageModel


class NewsRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> NewsModel:
        news = await db.execute(select(NewsModel).where(NewsModel.guid == guid).limit(1))
        return news.scalar()

    @staticmethod
    async def get_all(db: AsyncSession, tag: str, offset: int, limit: int = 100) -> List[NewsModel]:
        news = await db.execute(select(NewsModel).where(NewsModel.tag == tag)
                                .order_by(desc(NewsModel.date)).offset(offset).limit(limit))
        return news.scalars().unique().all()

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(NewsModel).where(NewsModel.guid == guid))
        await db.commit()
