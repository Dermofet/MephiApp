from typing import Optional

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.lesson_translate import LessonTranslateModel
from backend.schemas.lesson_translate import LessonTranslateCreateSchema


class LessonTranslateRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: LessonTranslateCreateSchema) -> LessonTranslateModel:
        lesson_tr = LessonTranslateModel(**schemas.dict())
        db.add(lesson_tr)
        await db.commit()
        await db.refresh(lesson_tr)
        return lesson_tr

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> LessonTranslateModel:
        lesson_tr = await db.execute(select(LessonTranslateModel).where(LessonTranslateModel.guid == guid).limit(1))
        return lesson_tr.scalar()

    @staticmethod
    async def get_unique(db: AsyncSession, type_: str, name: str, subgroup: Optional[str], lang: str) \
            -> LessonTranslateModel:
        lesson_tr = await db.execute(select(LessonTranslateModel).where(LessonTranslateModel.type == type_ and
                                                                        LessonTranslateModel.name == name and
                                                                        LessonTranslateModel.subgroup == subgroup and
                                                                        LessonTranslateModel.lang == lang).limit(1))
        return lesson_tr.scalar()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str, lang: str) -> LessonTranslateModel:
        lesson_tr = await db.execute(select(LessonTranslateModel).where(LessonTranslateModel.name == name and
                                                                        LessonTranslateModel.lang == lang).limit(1))
        return lesson_tr.scalar()

    @staticmethod
    async def get_by_lesson_guid(db: AsyncSession, guid: UUID4, lang: str) -> LessonTranslateModel:
        lesson_tr = await db.execute(select(LessonTranslateModel).where(LessonTranslateModel.lesson_guid == guid and
                                                                        LessonTranslateModel.lang == lang).limit(1))
        return lesson_tr.scalar()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: LessonTranslateCreateSchema) -> LessonTranslateModel:
        lesson_tr = await LanguageRepository.get_by_id(db, guid)

        if lesson_tr is None:
            HTTPException(status_code=404, detail="Перевод (занятие) не найден")

        lesson_tr = await db.execute(update(LessonTranslateModel).where(LessonTranslateModel.guid == guid)
                                     .values(**schemas.dict()))
        await db.commit()
        await db.refresh(lesson_tr)
        return lesson_tr

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(LessonTranslateModel).where(LessonTranslateModel.guid == guid))
        await db.commit()
