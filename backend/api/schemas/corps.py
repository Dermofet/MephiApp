from typing import Optional

from pydantic import ConfigDict, UUID4, BaseModel, Field

from backend.api.database.models.corps import CorpsModel


class CorpsBaseSchema(BaseModel):
    name: str = Field(description="Название корпуса")


class CorpsCreateSchema(CorpsBaseSchema):
    pass


class CorpsOutputSchema(CorpsBaseSchema):
    pass


class CorpsSchema(CorpsBaseSchema):
    guid: Optional[UUID4] = Field(description="ID")
    model_config = ConfigDict(from_attributes=True)

    def clone(self):
        return CorpsSchema(
            guid=self.guid,
            name=self.name
        )

    def to_model(self):
        return CorpsModel(
            guid=self.guid,
            name=self.name
        )
