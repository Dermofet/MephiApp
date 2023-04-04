from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.preview import PreviewRepository
from backend.schemas.preview import PreviewOutputSchema, PreviewSchema


class PreviewService:
    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> PreviewOutputSchema:
        preview = await PreviewRepository.get_by_id(db, guid)
        if preview is None:
            raise HTTPException(404, "Превью не найдена")
        return PreviewOutputSchema(**PreviewSchema.from_orm(preview).dict())

    @staticmethod
    async def get_all(db: AsyncSession, tag: str, offset: int = 0, limit: int = 100) -> dict[str, list[PreviewOutputSchema]]:
        previews = await PreviewRepository.get_all(db, tag, offset, limit)
        return {"previews": [PreviewOutputSchema(**PreviewSchema.from_orm(_).dict()) for _ in previews]}

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await PreviewRepository.delete(db, guid)
