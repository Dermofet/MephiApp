from typing import Optional

from pydantic import UUID4, BaseModel, Field, HttpUrl


class NewsImageBaseSchema(BaseModel):
    url: Optional[HttpUrl] = Field(description="Ссылка на картинку")
    text: Optional[str] = Field(description="Текст картинки")


class NewsImageOutputSchema(NewsImageBaseSchema):
    pass


class NewsImageSchema(NewsImageBaseSchema):
    guid: UUID4 = Field(description="ID")
    news_guid: UUID4 = Field(description="ID новости в системе")

    class Config:
        orm_mode = True
