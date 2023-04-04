from typing import List

from pydantic import UUID4
from sqlalchemy import delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.preview import PreviewModel


class PreviewRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> PreviewModel:
        preview = await db.execute(select(PreviewModel).where(PreviewModel.guid == guid).limit(1))
        return preview.scalar()

    @staticmethod
    async def get_all(db: AsyncSession, tag: str, offset: int = 0, limit: int = 100) -> List[PreviewModel]:
        previews = await db.execute(select(PreviewModel).where(PreviewModel.tag == tag)
                                    .order_by(desc(PreviewModel.date)).offset(offset).limit(limit))
        return previews.scalars().unique().all()

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(PreviewModel).where(PreviewModel.guid == guid))
        await db.commit()
