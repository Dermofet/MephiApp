from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.DataBase.Models.TeacherTranslate import TeacherTranslate
from backend.Schemas.TeacherTranslate import TeacherTranslateCreate, TeacherTranslateOutput


class TeacherTranslateRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: TeacherTranslateCreate) -> TeacherTranslate:
        teacher_tr = TeacherTranslate(**schemas.dict(exclude_unset=True))
        db.add(teacher_tr)
        await db.commit()
        await db.refresh(teacher_tr)
        return teacher_tr

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> TeacherTranslate:
        teacher_tr = await db.execute(select(TeacherTranslate).where(TeacherTranslate.guid == guid).limit(1))
        return teacher_tr.scalar()

    @staticmethod
    async def get_unique(db: AsyncSession, teacher_guid: UUID4, lang: str):
        teacher_tr = await db.execute(select(TeacherTranslate).where(TeacherTranslate.teacher_guid == teacher_guid and
                                                                     TeacherTranslate.lang == lang).limit(1))
        return teacher_tr.scalar()

    @staticmethod
    async def get_all_by_lang(db: AsyncSession, lang_guid: UUID4) -> List[TeacherTranslate]:
        teachers_tr = await db.execute(select(TeacherTranslate).where(TeacherTranslate.lang_guid == lang_guid))
        return teachers_tr.scalars().unique().all()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: TeacherTranslateCreate) -> TeacherTranslate:
        teacher_tr = await TeacherTranslateRepository.get_by_id(db, guid)

        if teacher_tr is None:
            HTTPException(status_code=404, detail="Перевод (преподаватель) не найден")

        teacher_tr = await db.execute(update(TeacherTranslate).where(TeacherTranslate.guid == guid).values(**schemas.dict()))
        await db.commit()
        await db.refresh(teacher_tr)
        return teacher_tr

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(TeacherTranslate).where(TeacherTranslate.guid == guid))
        await db.commit()
