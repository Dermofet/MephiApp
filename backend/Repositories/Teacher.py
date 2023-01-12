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
    async def create(db: AsyncSession, schemas: TeacherCreate, trans_guid: UUID4) -> Teacher:
        teacher = Teacher(**schemas.dict(exclude_unset=True), teacher_translate_guid=trans_guid)
        db.add(teacher)
        await db.commit()
        await db.refresh(teacher)
        return teacher

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> Teacher:
        teacher = await db.execute(select(Teacher).where(Teacher.guid == guid).limit(1))
        if len(teacher.scalars().all()) > 0:
            return teacher.scalars().all()[0]
        return None

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Teacher]:
        teachers = await db.execute(select(Teacher))
        return teachers.scalars().unique().all()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Teacher:
        teacher = await db.execute(select(Teacher)
                                   .join(TeacherTranslate,
                                         TeacherTranslate.name == name)
                                   .where(TeacherTranslate.guid == Teacher.teacher_translate_guid).limit(1))
        if len(teacher.scalars().all()) > 0:
            return teacher.scalars().all()[0]
        return None

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
