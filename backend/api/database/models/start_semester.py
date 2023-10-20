import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.api.database.connection import Base


class StartSemesterModel(Base):
    __tablename__ = "start_semester"
    __table_args__ = {"extend_existing": True}

    guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    date: Mapped[datetime.date]
