from typing import Dict, List

from fastapi import HTTPException, Response
from pydantic import UUID4

from backend.api.schemas.news import NewsOutputSchema, NewsSchema
from backend.api.services.base_servise import BaseService


class NewsService(BaseService):
    async def get(self, guid: UUID4) -> NewsOutputSchema:
        news = await self.facade.get_by_id_news(guid)
        if news is None:
            raise HTTPException(404, "Новость не найдена")
        return NewsOutputSchema(**NewsSchema.model_validate(news).model_dump())

    async def get_all(self, tag: str, offset: int, limit: int = 100) -> Dict[str, List[NewsOutputSchema]]:
        news = await self.facade.get_all_news(tag, offset, limit)
        return {"news": [NewsOutputSchema(**NewsSchema.model_validate(_).model_dump()) for _ in news]}

    async def delete(self, guid: UUID4) -> Response:
        await self.facade.delete_news(guid)
        await self.facade.commit()

        return Response(status_code=204)
