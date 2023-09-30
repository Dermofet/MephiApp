from typing import Dict, List, Optional

from pydantic import Field, field_validator

from etl.schemas.base import Base


class TeacherTranslateLoading(Base):
    lang: str = Field(description="Код страны (для перевода)")
    name: str = Field(description="ФИО приподавателя")
    fullname: Optional[str] = Field(description="Полное ФИО преподавателя")

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


class TeacherLoading(Base):
    url: Optional[str] = Field(description="Ссылка на дискорд")
    alt_url: Optional[str] = Field(description="Ссылка на дискорд")
    trans: List[TeacherTranslateLoading] = Field(description="Список переводов") 

    def __hash__(self):
        return hash(self.trans[0].name)

    def __eq__(self, other):
        return self.trans[0].name == other.trans[0].name

class TeacherFullnameLoading(Base):
    url: Optional[str] = Field(description="Ссылка на дискорд")
    alt_url: Optional[str] = Field(description="Ссылка на дискорд")

    lang: str = Field(description="Код страны (для перевода)")
    name: Optional[str] = Field(description="ФИО приподавателя")
    fullname: str = Field(description="Полное ФИО преподавателя")

    def __hash__(self):
        return hash(self.fullname)

    def __eq__(self, other):
        return self.fullname == other.fullname

    @field_validator("name", mode="before")
    def set_name(cls, v: str, values: Dict[str, str]):
        if isinstance(v, str):
            return v

        fullname = values.get("fullname")
        if not fullname:
            return None

        parts = fullname.split(" ")
        return f"{parts[0]} {parts[1][0]}.{parts[2][0]}." if len(parts) == 3 else f"{parts[0]} {parts[1][0]}."