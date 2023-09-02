import uuid

from sqlalchemy import Column, Date, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.database.connection import Base


class NewsModel(Base):
    __tablename__ = "news"
    __table_args__ = {'extend_existing': True}

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    news_id = Column(String(50), unique=True)

    title = Column(String)
    preview_url = Column(String, nullable=True)
    date = Column(Date)
    text = Column(Text)
    tag = Column(String(100))

    imgs = relationship("NewsImageModel", back_populates="news", lazy="joined", uselist=True)

    def hash(self):
        return hash(self.news_id)

    def eq(self, other):
        if isinstance(v, NewsModel):
            return self.news_id == other.news_id
        return False
