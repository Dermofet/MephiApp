from typing import Optional

from pydantic import Field

from etl.schemas.base import Base


class NewsImageLoading(Base):
    url: str = Field(description="Ссылка на картинку")
    text: Optional[str] = Field(description="Текст картинки")
