import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.api.schemas.news_img import NewsImageCreateSchema, NewsImageOutputSchema, NewsImageSchema


class NewsBaseSchema(BaseModel):
    title: str = Field(description="Текст превью")
    preview_url: Optional[str] = Field(description="Ссылка на картинку")
    date: datetime.date = Field(description="Дата публикации новости")
    text: str = Field(description="Текст новости")

    @field_validator("date", mode="before")
    def change_date_start(cls, value):
        if isinstance(value, str):
            date_ = value.split(".")
            date_.reverse()
            return "-".join(date_)
        return None


class NewsCreateSchema(NewsBaseSchema):
    news_id: str = Field(description="ID новости")
    imgs: List[NewsImageCreateSchema] = Field(description="Список картинок новости")


class NewsOutputSchema(NewsBaseSchema):
    date: str = Field(description="Дата публикации новости")
    imgs: List[NewsImageOutputSchema] = Field(description="Список картинок новости")


class NewsSchema(NewsBaseSchema):
    date: str = Field(description="Дата публикации новости")
    imgs: List[NewsImageSchema] = Field(description="Список картинок новости")

    @field_validator("date", mode="before")
    def change_date_start(cls, value):
        if isinstance(value, datetime.date):
            return value.strftime("%m.%d.%Y")
        elif isinstance(value, str):
            return value
        elif isinstance(value, type(None)):
            return None
        else:
            ValueError(f"date_start - неверный тип данных. Ожидалось date, было получено {type(value)}")

    model_config = ConfigDict(from_attributes=True)
