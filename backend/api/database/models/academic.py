import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.api.database.connection import Base


class AcademicModel(Base):
    __tablename__ = "academics"

    guid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

    groups: Mapped["GroupModel"] = relationship("GroupModel", back_populates="academic", lazy='joined')
