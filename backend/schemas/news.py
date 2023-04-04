from pydantic import UUID4, BaseModel, Field

from backend.schemas.news_img import NewsImageOutputSchema, NewsImageSchema


class NewsBaseSchema(BaseModel):
    news_text: str = Field(description="Текст новости")


class NewsOutputSchema(NewsBaseSchema):
    news_imgs: list[NewsImageOutputSchema] = Field(description="Список картинок новости")


class NewsSchema(NewsBaseSchema):
    guid: UUID4 = Field(description="ID")
    news_id: str = Field(description="ID новости на сайте")
    news_imgs: list[NewsImageSchema] = Field(description="Список картинок новости")

    class Config:
        orm_mode = True
