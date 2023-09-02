import datetime
import uuid
from typing import List, Optional

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.api.database.connection import Base


class NewsModel(Base):
    __tablename__ = "news"

    guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    news_id: Mapped[str] = mapped_column(String(50), unique=True)

    title: Mapped[str]
    preview_url: Mapped[Optional[str]]
    date: Mapped[datetime.date]
    text: Mapped[str] = mapped_column(Text)
    tag: Mapped[str] = mapped_column(String(100))

    imgs: Mapped[List["NewsImageModel"]] = relationship("NewsImageModel", back_populates="news", lazy="joined")
