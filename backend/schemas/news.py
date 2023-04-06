import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, Field, HttpUrl, validator

from backend.schemas.news_img import NewsImageOutputSchema, NewsImageSchema


class NewsBaseSchema(BaseModel):
    title: str = Field(description="Текст превью")
    preview_url: Optional[HttpUrl] = Field(description="Ссылка на картинку")
    date: datetime.date = Field(description="Дата публикации новости")
    text: str = Field(description="Текст новости")

    @validator("date", pre=True)
    def change_date_start(cls, value):
        if isinstance(value, str):
            date_ = value.split('.')
            date_.reverse()
            return "-".join(date_)
        return None


class NewsOutputSchema(NewsBaseSchema):
    date: str = Field(description="Дата публикации новости")
    imgs: list[NewsImageOutputSchema] = Field(description="Список картинок новости")


class NewsSchema(NewsBaseSchema):
    date: str = Field(description="Дата публикации новости")
    imgs: list[NewsImageSchema] = Field(description="Список картинок новости")

    @validator("date", pre=True)
    def change_date_start(cls, value):
        if isinstance(value, datetime.date):
            return value.strftime('%m.%d.%Y')
        elif isinstance(value, str):
            return value
        elif isinstance(value, type(None)):
            return None
        else:
            ValueError(f"date_start - неверный тип данных. Ожидалось date, было получено {type(value)}")

    class Config:
        orm_mode = True
