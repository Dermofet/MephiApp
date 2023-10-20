from pydantic import Field

from etl.schemas.base import Base


class AcademicLoading(Base):
    name: str = Field(..., description="Название")

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name
