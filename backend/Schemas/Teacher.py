from typing import Optional

from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session

from backend.Schemas.TeacherTranslate import TeacherTranslateOutput


class TeacherBase(BaseModel):
    online_url: str = Field(description="Ссылка на онлайн аудиторию")
    alt_online_url: str = Field(description="Ссылка на альтернативную онлайн аудиторию")


class TeacherCreate(TeacherBase):
    lang: Optional[str] = Field(description="Код страны (для перевода)")
    name: Optional[str] = Field(description="ФИО приподавателя")
    fullname: Optional[str] = Field(description="Полное ФИО преподавателя")


class TeacherOutput(TeacherBase):
    trans: TeacherTranslateOutput = Field(description="Переведенные поля модели")

    class Config:
        orm_mode = True

class Teacher(TeacherBase):
    guid: UUID4 = Field(description="ID")
    trans: TeacherTranslateOutput = Field(description="Переведенные поля модели")

    class Config:
        orm_mode = True
