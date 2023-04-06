import uuid

from sqlalchemy import UUID, Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from backend.database.connection import Base


class NewsImageModel(Base):
    __tablename__ = "news_image"
    __table_args__ = {'extend_existing': True}

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    url = Column(String, nullable=True)
    text = Column(Text, nullable=True)
    news_guid = Column(UUID(as_uuid=True), ForeignKey("news.guid"))

    news = relationship("NewsModel", back_populates="imgs", lazy="joined")

    def __hash__(self):
        return hash(str(self.url) + str(self.text))

    def eq(self, other):
        if isinstance(other, NewsImageModel):
            return self.url == other.url and self.text == other.text
        return False
