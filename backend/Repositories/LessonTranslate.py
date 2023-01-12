from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.DataBase.Models.LessonTranslate import LessonTranslate
from backend.Schemas.LessonTranslate import LessonTranslateCreate, LessonTranslateOutput


class LessonTranslateRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: LessonTranslateCreate) -> LessonTranslate:
        lesson_tr = LessonTranslate(**schemas.dict(exclude_unset=True))
        db.add(lesson_tr)
        await db.commit()
        await db.refresh(lesson_tr)
        return lesson_tr

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> LessonTranslate:
        lesson_tr = await db.execute(select(LessonTranslate).where(LessonTranslate.guid == guid).limit(1))
        if len(lesson_tr.scalars().all()) > 0:
            return lesson_tr.scalars().all()[0]
        return None

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: LessonTranslateCreate) -> LessonTranslate:
        lesson_tr = await LanguageRepository.get_by_id(db, guid)

        if lesson_tr is None:
            HTTPException(status_code=404, detail="Перевод (занятие) не найден")

        lesson_tr = await db.execute(update(LessonTranslate).where(LessonTranslate.guid == guid).values(**schemas.dict()))
        await db.commit()
        await db.refresh(lesson_tr)
        return lesson_tr

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(LessonTranslate).where(LessonTranslate.guid == guid))
        await db.commit()
