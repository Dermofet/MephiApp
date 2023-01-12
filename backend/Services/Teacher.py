from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.Repositories.Language import LanguageRepository
from backend.Repositories.Teacher import TeacherRepository
from backend.Repositories.TeacherTranslate import TeacherTranslateRepository
from backend.Schemas.Language import LanguageCreate
from backend.Schemas.Teacher import TeacherCreate, TeacherOutput
from backend.Schemas.TeacherTranslate import TeacherTranslateCreate


class TeacherService:
    @staticmethod
    async def create(db: AsyncSession, schemas: TeacherCreate) -> TeacherOutput:
        teacher = await TeacherRepository.get_by_name(db, schemas)
        if teacher is not None:
            raise HTTPException(409, "Преподаватель уже существует")
        else:
            language = await LanguageRepository.create(db, LanguageCreate(lang=schemas.lang))
            teacher_translate = await TeacherTranslateRepository.create(db, TeacherTranslateCreate(
                name=schemas.name, fullname=schemas.fullname), lang_guid=language.guid)
            teacher = await TeacherRepository.create(db, schemas, trans_guid=teacher_translate.guid)
        return TeacherOutput.from_orm(teacher)

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> TeacherOutput:
        teacher = await TeacherRepository.get_by_id(db, guid)
        if teacher is None:
            raise HTTPException(404, "Преподаватель не найден")
        return TeacherOutput.from_orm(teacher)

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> TeacherOutput:
        teacher = await TeacherRepository.get_by_name(db, name)
        if teacher is None:
            raise HTTPException(404, "Преподаватель не найден")
        return TeacherOutput.from_orm(teacher)

    @staticmethod
    async def get_all(db: AsyncSession) -> list[str]:
        teachers = await TeacherRepository.get_all(db)
        if teachers is None:
            raise HTTPException(404, "Преподаватель не найден")
        return [TeacherOutput.from_orm(teacher).trans.fullname for teacher in teachers]

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: TeacherCreate) -> TeacherOutput:
        teacher = await TeacherRepository.update(db, guid, schemas)
        if teacher is None:
            raise HTTPException(404, "Преподаватель не найден")
        return TeacherOutput.from_orm(teacher)

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await TeacherRepository.delete(db, guid)
        return Response(status_code=204)
