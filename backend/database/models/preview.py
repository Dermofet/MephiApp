import uuid

from sqlalchemy import UUID, VARCHAR, Column, Date, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from backend.database.connection import Base


class PreviewModel(Base):
    __tablename__ = "preview"
    __table_args__ = {'extend_existing': True}

    guid = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    url = Column(String, nullable=True)
    text = Column(Text, nullable=True)
    date = Column(Date)
    tag = Column(String(50))
    news_guid = Column(UUID(as_uuid=True), ForeignKey("news.guid"))

    news = relationship("NewsModel", back_populates="preview", lazy="joined")

    def __hash__(self):
        return hash(str(self.url) + str(self.text) + str(self.date) + str(self.tag))

    def eq(self, other):
        if isinstance(other, PreviewModel):
            return self.url == other.url and self.text == other.text and self.date == other.date and \
                   self.tag == other.tag
        return False
