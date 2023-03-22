from copy import deepcopy
from typing import Optional

from pydantic import UUID4, BaseModel, Field, validator
from sqlalchemy.orm import Session

from backend.database.models.teacher import TeacherModel
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
    guid: Optional[UUID4] = Field(description="ID")
    trans: TeacherTranslateSchema = Field(description="Поля, нуждающиеся в переводе")

    def clone(self):
        return TeacherSchema(
            guid=self.guid,
            online_url=self.online_url,
            alt_online_url=self.alt_online_url,
            trans=[self.trans.clone()]
        )

    def to_model(self):
        return TeacherModel(
            guid=self.guid,
            online_url=self.online_url,
            alt_online_url=self.alt_online_url,
            trans=[self.trans.to_model(self.guid)]
        )

    def __eq__(self, other):
        if isinstance(other, TeacherSchema):
            return self.trans.name == other.trans.name and self.trans.fullname == other.trans.fullname and \
                   self.trans.lang == self.trans.lang
        return False

    def __hash__(self):
        return hash(str(self.trans.name) + str(self.trans.fullname) + str(self.trans.lang))

    @validator("trans", pre=True)
    def check_trans(cls, trans):
        if isinstance(trans, list):
            for tr in trans:
                if isinstance(tr, (TeacherTranslateSchema, TeacherTranslateModel)):
                    return tr
                else:
                    raise ValueError(f"trans содержит не TeacherTranslateSchema, type(trans) {type(trans)}")
        else:
            raise ValueError("trans - не список")

    class Config:
        orm_mode = True
