import time
from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.teacher import TeacherModel
from backend.database.models.teacher_translate import TeacherTranslateModel
from backend.repositories.teacher_translate import TeacherTranslateRepository
from backend.schemas.teacher import TeacherCreateSchema


class TeacherRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: TeacherCreateSchema) -> TeacherModel:
        teacher = TeacherModel(online_url=schemas.online_url, alt_online_url=schemas.alt_online_url)
        db.add(teacher)
        await db.commit()
        await db.refresh(teacher)
        return teacher

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> TeacherModel:
        teacher = await db.execute(select(TeacherModel).where(TeacherModel.guid == guid).limit(1))
        return teacher.scalar()

    @staticmethod
    async def get_all(db: AsyncSession, lang: str) -> List[TeacherModel]:
        teachers_translate = await db.execute(select(TeacherModel)
                                              .join(TeacherTranslateModel,
                                                    TeacherModel.guid == TeacherTranslateModel.teacher_guid)
                                              .where(TeacherTranslateModel.lang == lang))
        return teachers_translate.scalars().unique().all()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str, lang: str) -> TeacherModel:
        teacher = await db.execute(select(TeacherModel)
                                   .join(TeacherTranslateModel,
                                         TeacherTranslateModel.teacher_guid == TeacherModel.guid)
                                   .where(TeacherTranslateModel.name == name,
                                          TeacherTranslateModel.lang == lang).limit(1))
        return teacher.scalar()

    @staticmethod
    async def get_unique(db: AsyncSession, schemas: TeacherCreateSchema) -> TeacherModel:
        teacher = await db.execute(select(TeacherModel)
                                   .join(TeacherTranslateModel,
                                         TeacherTranslateModel.teacher_guid == TeacherModel.guid)
                                   .where(TeacherModel.online_url == schemas.online_url and
                                          TeacherModel.alt_online_url == schemas.alt_online_url and
                                          TeacherTranslateModel.name == schemas.name and
                                          TeacherTranslateModel.lang == schemas.lang and
                                          TeacherTranslateModel.fullname == schemas.fullname).limit(1))
        return teacher.scalar()

    @staticmethod
    async def update(db: AsyncSession, schemas: TeacherCreateSchema) -> TeacherModel:
        teacher = await TeacherRepository.get_by_name(db, name=schemas.name, lang=schemas.lang)

        if teacher is None:
            raise HTTPException(404, "Преподавателя не существует")

        await db.execute(update(TeacherTranslateModel)
                         .where(TeacherTranslateModel.teacher_guid == teacher.guid)
                         .values(name=schemas.name,
                                 fullname=schemas.fullname,
                                 lang=schemas.lang,
                                 teacher_guid=teacher.guid))
        await db.execute(update(TeacherModel).where(TeacherModel.guid == teacher.guid)
                         .values(online_url=schemas.online_url,
                                 alt_online_url=schemas.alt_online_url))

        await db.commit()
        await db.refresh(teacher)

        return teacher

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(TeacherModel).where(TeacherModel.guid == guid))
        await db.commit()
