import datetime
from typing import List, Optional

from pydantic import Field, field_validator

from etl.schemas.base import Base
from etl.schemas.news_img import NewsImageLoading


class NewsLoading(Base):
    news_id: str = Field(..., description="ID новости")
    title: str = Field(..., description="Текст превью")
    preview_url: Optional[str] = Field(None, description="Ссылка на изображение превью")
    date: datetime.date = Field(..., description="Дата публикации новости")
    text: str = Field(..., description="Текст новости")
    tag: str = Field(..., description="Тэг новости")
    imgs: List[NewsImageLoading] = Field(..., description="Список изображений новости")

    @field_validator("date", mode="before")
    def change_date_start(cls, value):
        if isinstance(value, str):
            date_ = value.split(".")
            date_.reverse()
            return "-".join(date_)
        return None

    def __hash__(self) -> int:
        return hash(self.news_id)

    def __eq__(self, other) -> bool:
        return self.news_id == other.news_id
