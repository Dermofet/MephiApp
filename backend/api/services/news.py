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
        return {
            "news": [
                NewsOutputSchema(
                    **NewsSchema(
                        title=n.title,
                        preview_url=n.preview_url,
                        date=n.date,
                        text=n.text,
                        imgs=await self.facade.get_images_news(n),
                    ).model_dump()
                )
                for n in news
            ],
        }

    async def delete(self, guid: UUID4) -> Response:
        await self.facade.delete_news(guid)
        await self.facade.commit()

        return Response(status_code=204)
