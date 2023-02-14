from typing import Optional

from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session


class TeacherBaseSchema(BaseModel):
    online_url: Optional[str] = Field(description="Ссылка на онлайн аудиторию")
    alt_online_url: Optional[str] = Field(description="Ссылка на альтернативную онлайн аудиторию")


class TeacherCreateSchema(TeacherBaseSchema):
    lang: str = Field(description="Код страны (для перевода)")
    name: str = Field(description="ФИО приподавателя")
    fullname: Optional[str] = Field(description="Полное ФИО преподавателя")


class TeacherOutputSchema(TeacherBaseSchema):
    pass


class TeacherSchema(TeacherBaseSchema):
    guid: UUID4 = Field(description="ID")

    class Config:
        orm_mode = True
