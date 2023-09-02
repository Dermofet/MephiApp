from typing import Optional

from pydantic import ConfigDict, UUID4, BaseModel, Field


class NewsImageBaseSchema(BaseModel):
    url: Optional[str] = Field(description="Ссылка на картинку")
    text: Optional[str] = Field(description="Текст картинки")


class NewsImageCreateSchema(NewsImageBaseSchema):
    pass


class NewsImageOutputSchema(NewsImageBaseSchema):
    pass


class NewsImageSchema(NewsImageBaseSchema):
    guid: UUID4 = Field(description="ID")
    news_guid: UUID4 = Field(description="ID новости в системе")
    model_config = ConfigDict(from_attributes=True)
