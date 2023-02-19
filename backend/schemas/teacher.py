from typing import Optional

from pydantic import UUID4, BaseModel, Field, validator
from sqlalchemy.orm import Session

from backend.database.models.teacher_translate import TeacherTranslateModel
from backend.schemas.teacher_translate import TeacherTranslateOutputSchema, TeacherTranslateSchema


class TeacherBaseSchema(BaseModel):
    online_url: Optional[str] = Field(description="Ссылка на онлайн аудиторию")
    alt_online_url: Optional[str] = Field(description="Ссылка на альтернативную онлайн аудиторию")


class TeacherCreateSchema(TeacherBaseSchema):
    lang: str = Field(description="Код страны (для перевода)")
    name: str = Field(description="ФИО приподавателя")
    fullname: Optional[str] = Field(description="Полное ФИО преподавателя")


class TeacherOutputSchema(TeacherBaseSchema):
    trans: TeacherTranslateOutputSchema = Field(description="Поля, нуждающиеся в переводе")


class TeacherSchema(TeacherBaseSchema):
    guid: UUID4 = Field(description="ID")
    trans: TeacherTranslateSchema = Field(description="Поля, нуждающиеся в переводе")

    @validator("trans", pre=True)
    def check_trans(cls, trans):
        if isinstance(trans, list):
            for tr in trans:
                if isinstance(tr, TeacherTranslateModel):
                    return tr
                else:
                    raise ValueError("trans содержит не TeacherTranslateModel")
        else:
            raise ValueError("trans - не список")

    class Config:
        orm_mode = True
