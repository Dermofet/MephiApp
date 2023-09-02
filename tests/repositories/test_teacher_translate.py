from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.teacher_translate import TeacherTranslateModel
from backend.schemas.teacher_translate import TeacherTranslateCreateSchema


class TeacherTranslateRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: TeacherTranslateCreateSchema) -> TeacherTranslateModel:
        teacher_tr = TeacherTranslateModel(**schemas.dict())
        db.add(teacher_tr)
        await db.commit()
        await db.refresh(teacher_tr)
        return teacher_tr

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> TeacherTranslateModel:
        teacher_tr = await db.execute(select(TeacherTranslateModel).where(TeacherTranslateModel.guid == guid).limit(1))
        return teacher_tr.scalar()

    @staticmethod
    async def get_unique(db: AsyncSession, teacher_guid: UUID4, lang: str) -> TeacherTranslateModel:
        teacher_tr = await db.execute(
            select(TeacherTranslateModel).where(TeacherTranslateModel.teacher_guid == teacher_guid,
                                                TeacherTranslateModel.lang == lang).limit(1))
        return teacher_tr.scalar()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> TeacherTranslateModel:
        teacher_tr = await db.execute(select(TeacherTranslateModel).where(TeacherTranslateModel.name == name).limit(1))
        return teacher_tr.scalar()

    @staticmethod
    async def get_all_by_lang(db: AsyncSession, lang: str) -> List[TeacherTranslateModel]:
        teachers_tr = await db.execute(select(TeacherTranslateModel).where(TeacherTranslateModel.lang == lang))
        return teachers_tr.scalars().unique().all()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: TeacherTranslateCreateSchema) -> TeacherTranslateModel:
        teacher_tr = await TeacherTranslateRepository.get_by_id(db, guid)

        if teacher_tr is None:
            HTTPException(status_code=404, detail="Перевод (преподаватель) не найден")

        teacher_tr = await db.execute(
            update(TeacherTranslate).where(TeacherTranslate.guid == guid).values(**schemas.dict()))
        await db.commit()
        await db.refresh(teacher_tr)
        return teacher_tr

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(TeacherTranslate).where(TeacherTranslate.guid == guid))
        await db.commit()
