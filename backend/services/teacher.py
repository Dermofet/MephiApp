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
    async def create(db: AsyncSession, schemas: TeacherCreateSchema) -> TeacherTranslateOutputSchema:
        teacher = await TeacherRepository.get_by_name(db, schemas.name, schemas.lang)
        if teacher is not None:
            raise HTTPException(409, "Преподаватель уже существует")
        else:
            teacher = await TeacherRepository.create(db, schemas)
            teacher_translate = await TeacherTranslateRepository.create(db, TeacherTranslateCreateSchema(
                name=schemas.name,
                fullname=schemas.fullname,
                lang=schemas.lang,
                teacher_guid=teacher.guid))
        return TeacherTranslateOutputSchema(**TeacherTranslateSchema.from_orm(teacher_translate).dict())

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> TeacherOutputSchema:
        teacher = await TeacherRepository.get_by_id(db, guid)
        if teacher is None:
            raise HTTPException(404, "Преподаватель не найден")
        return TeacherOutputSchema(**TeacherSchema.from_orm(teacher).dict())

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> TeacherTranslateOutputSchema:
        teacher_translate = await TeacherTranslateRepository.get_by_name(db, name)
        if teacher_translate is None:
            raise HTTPException(404, "Преподаватель не найден")
        return TeacherTranslateOutputSchema(**TeacherTranslateSchema.from_orm(teacher_translate).dict())

    @staticmethod
    async def get_all(db: AsyncSession, lang: str) -> list[str]:
        teachers = await TeacherTranslateRepositorySchema.get_all_by_lang(db, lang)
        return [TeacherTranslateSchema.from_orm(teacher).name for teacher in teachers]

    @staticmethod
    async def update(db: AsyncSession, schemas: TeacherCreateSchema) -> TeacherTranslateOutputSchema:
        teacher = await TeacherRepository.update(db, schemas)
        if teacher is None:
            raise HTTPException(404, "Преподаватель не найден")
        return TeacherTranslateOutputSchema(**TeacherTranslateSchema.from_orm(teacher).dict())

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await TeacherRepository.delete(db, guid)
        return Response(status_code=204)
