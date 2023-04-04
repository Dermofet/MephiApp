from typing import Optional

from pydantic import UUID4, BaseModel, Field

from backend.database.models.teacher_translate import TeacherTranslateModel


class TeacherTranslateBaseSchema(BaseModel):
    name: str = Field(description="Краткое ФИО")
    fullname: Optional[str] = Field(description="Полное ФИО")
    lang: str = Field(description="Код языка")


class TeacherTranslateCreateSchema(TeacherTranslateBaseSchema):
    teacher_guid: UUID4 = Field(description="ID преподавателя")


class TeacherTranslateOutputSchema(TeacherTranslateBaseSchema):
    pass


class TeacherTranslateSchema(TeacherTranslateBaseSchema):
    guid: Optional[UUID4] = Field(description="ID")

    def clone(self):
        return TeacherTranslateSchema(
            guid=self.guid,
            name=self.name,
            fullname=self.fullname,
            lang=self.lang
        )

    def to_model(self, teacher_guid: UUID4):
        return TeacherTranslateModel(
            guid=self.guid,
            name=self.name,
            fullname=self.fullname,
            lang=self.lang,
            teacher_guid=teacher_guid
        )

    class Config:
        orm_mode = True
