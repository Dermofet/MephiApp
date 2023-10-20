from typing import Optional

from pydantic import UUID4, BaseModel, ConfigDict, Field

from backend.api.database.models.group import GroupModel
from backend.api.schemas.academic import AcademicOutputSchema, AcademicSchema


class GroupBaseSchema(BaseModel):
    name: str = Field(description="Название группы")
    course: int = Field(description="Курс обучения")


class GroupCreateSchema(GroupBaseSchema):
    academic: str = Field(description="Ученое звание")


class GroupOutputSchema(GroupBaseSchema):
    academic: AcademicOutputSchema = Field(description="Ученое звание")


class GroupSchema(GroupBaseSchema):
    guid: Optional[UUID4] = Field(description="ID")
    academic: AcademicSchema = Field(description="Ученое звание")
    model_config = ConfigDict(from_attributes=True)

    def clone(self):
        return GroupSchema(name=self.name, course=self.course, academic=self.academic.clone())

    def to_model(self):
        return GroupModel(
            name=self.name,
            course=self.course,
            academic_guid=self.academic.guid,
            academic=self.academic.to_model() if self.academic.guid is None else None,
        )

    def __eq__(self, other):
        return self.name == other.name if isinstance(other, GroupSchema) else False

    def __hash__(self):
        return hash(self.name)
