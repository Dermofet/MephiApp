from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.teacher import TeacherRepository
from backend.repositories.teacher_translate import TeacherTranslateRepository
from backend.schemas.teacher import TeacherCreateSchema, TeacherOutputSchema, TeacherSchema
from backend.schemas.teacher_translate import (
    TeacherTranslateCreateSchema,
    TeacherTranslateOutputSchema,
    TeacherTranslateSchema,
)


class TeacherService:
    @staticmethod
    async def create(db: AsyncSession, schemas: TeacherCreateSchema) -> TeacherOutputSchema:
        teacher = await TeacherRepository.get_by_name(db, schemas.name, schemas.lang)
        if teacher is not None:
            raise HTTPException(409, "Преподаватель уже существует")
        else:
            teacher = await TeacherRepository.create(db, schemas)
            await TeacherTranslateRepository.create(db, TeacherTranslateCreateSchema(
                name=schemas.name,
                fullname=schemas.fullname,
                lang=schemas.lang,
                teacher_guid=teacher.guid))
            await db.refresh(teacher)
        return TeacherOutputSchema(**TeacherSchema.from_orm(teacher).dict())

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> TeacherOutputSchema:
        teacher = await TeacherRepository.get_by_id(db, guid)
        if teacher is None:
            raise HTTPException(404, "Преподаватель не найден")
        return TeacherOutputSchema(**TeacherSchema.from_orm(teacher).dict())

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str, lang: str) -> TeacherOutputSchema:
        teacher = await TeacherRepository.get_by_name(db, name, lang)
        print(TeacherOutputSchema(**TeacherSchema.from_orm(teacher).dict()))
        if teacher is None:
            raise HTTPException(404, "Преподаватель не найден")
        return TeacherOutputSchema(**TeacherSchema.from_orm(teacher).dict())

    @staticmethod
    async def get_all(db: AsyncSession, lang: str) -> list[str]:
        teachers = await TeacherRepository.get_all(db, lang)
        trans = [TeacherSchema.from_orm(teacher).trans for teacher in teachers]
        res = []
        for translate in trans:
            for teacher_translate in translate:
                if teacher_translate.lang == lang:
                    res.append(teacher_translate.name)
        return res

    @staticmethod
    async def update(db: AsyncSession, schemas: TeacherCreateSchema) -> TeacherOutputSchema:
        teacher = await TeacherRepository.update(db, schemas)
        if teacher is None:
            raise HTTPException(404, "Преподаватель не найден")
        return TeacherOutputSchema(**TeacherSchema.from_orm(teacher).dict())

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await TeacherRepository.delete(db, guid)
        return Response(status_code=204)
