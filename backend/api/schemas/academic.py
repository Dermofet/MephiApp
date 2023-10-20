from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field

from backend.api.database.models.academic import AcademicModel


class AcademicBaseSchema(BaseModel):
    name: str = Field(description="Ученое звание")


class AcademicCreateSchema(AcademicBaseSchema):
    pass


class AcademicOutputSchema(AcademicBaseSchema):
    pass


class AcademicSchema(AcademicBaseSchema):
    guid: Optional[UUID4] = Field(description="ID")
    model_config = ConfigDict(from_attributes=True)

    def clone(self):
        return AcademicSchema(guid=self.guid, name=self.name)

    def to_model(self):
        return AcademicModel(guid=self.guid, name=self.name)
