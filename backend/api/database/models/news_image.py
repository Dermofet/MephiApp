import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.api.database.connection import Base


class NewsImageModel(Base):
    __tablename__ = "news_image"

    guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    url: Mapped[Optional[str]]
    text: Mapped[Optional[str]] = mapped_column(Text)
    news_guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("news.guid"))

    news: Mapped["NewsModel"] = relationship(back_populates="imgs")
