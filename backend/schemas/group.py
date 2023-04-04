from typing import Optional

from pydantic import UUID4, BaseModel, Field

from backend.database.models.group import GroupModel
from backend.schemas.academic import AcademicOutputSchema, AcademicSchema


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

    class Config:
        orm_mode = True

    def clone(self):
        return GroupSchema(
            name=self.name,
            course=self.course,
            academic=self.academic.clone()
        )

    def to_model(self):
        return GroupModel(
            name=self.name,
            course=self.course,
            academic_guid=self.academic.guid,
            academic=self.academic.to_model() if self.academic.guid is None else None
        )

    def __eq__(self, other):
        if isinstance(other, GroupSchema):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)
