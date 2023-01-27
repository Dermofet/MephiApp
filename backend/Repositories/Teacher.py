from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.DataBase.Models.Teacher import Teacher
from backend.DataBase.Models.TeacherTranslate import TeacherTranslate
from backend.Schemas.Teacher import TeacherCreate


class TeacherRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: TeacherCreate) -> Teacher:
        teacher = Teacher(online_url=schemas.online_url, alt_online_url=schemas.alt_online_url)
        db.add(teacher)
        await db.commit()
        await db.refresh(teacher)
        return teacher

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> Teacher:
        teacher = await db.execute(select(Teacher).where(Teacher.guid == guid).limit(1))
        return teacher.scalar()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Teacher]:
        teachers = await db.execute(select(Teacher).join(TeacherTranslate, Teacher.guid == TeacherTranslate.teacher_guid))
        return teachers.scalars().unique().all()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str, lang: str) -> Teacher:
        teacher = await db.execute(select(Teacher)
                                   .join(TeacherTranslate,
                                         TeacherTranslate.name == name,
                                         TeacherTranslate.lang == lang)
                                   .where(Teacher.guid == TeacherTranslate.teacher_guid).limit(1))
        return teacher.scalar()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: TeacherCreate) -> Teacher:
        teacher = await RoomRepository.get_by_id(db, guid)

        if teacher is None:
            HTTPException(status_code=404, detail="Преподаватель не найден")

        teacher = await db.execute(update(Teacher).where(Teacher.guid == guid).values(**schemas.dict()))
        await db.commit()
        await db.refresh(teacher)
        return teacher

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(Teacher).where(Teacher.guid == guid))
        await db.commit()
