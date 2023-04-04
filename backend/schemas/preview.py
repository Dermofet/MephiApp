import datetime
from typing import Optional

from pydantic import UUID4, BaseModel, Field, HttpUrl, validator


class PreviewBaseSchema(BaseModel):
    url: Optional[HttpUrl] = Field(description="Ссылка на картинку")
    text: str = Field(description="Текст превью")
    date: datetime.date = Field(description="Дата публикации новости")
    news_guid: UUID4 = Field(description="ID новости в системе")

    @validator("date", pre=True)
    def change_date_start(cls, value):
        if isinstance(value, str):
            date_ = value.split('.')
            date_.reverse()
            return "-".join(date_)
        return None


class PreviewOutputSchema(PreviewBaseSchema):
    date: Optional[str] = Field(description="Дата публикации новости")


class PreviewSchema(PreviewBaseSchema):
    date: Optional[str] = Field(description="Дата публикации новости")

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
