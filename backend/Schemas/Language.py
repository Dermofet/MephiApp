from pydantic import UUID4, BaseModel, Field
from sqlalchemy.orm import Session


class LanguageBase(BaseModel):
    lang: str = Field(description="Код языка")


class LanguageCreate(LanguageBase):
    pass


class LanguageOutput(LanguageBase):

    class Config:
        orm_mode = True


class Language(LanguageBase):
    guid: UUID4 = Field(description="ID")

    class Config:
        orm_mode = True
