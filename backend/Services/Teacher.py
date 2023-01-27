from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

# from backend.Repositories.Language import LanguageRepository
from backend.Repositories.Teacher import TeacherRepository
from backend.Repositories.TeacherTranslate import TeacherTranslateRepository

# from backend.Schemas.Language import LanguageCreate
from backend.Schemas.Teacher import Teacher, TeacherCreate, TeacherOutput
from backend.Schemas.TeacherTranslate import TeacherTranslateCreate


class TeacherService:
    @staticmethod
    async def create(db: AsyncSession, schemas: TeacherCreate) -> TeacherOutput:
        teacher = await TeacherRepository.get_by_name(db, schemas, lang=schemas.lang)
        if teacher is not None:
            raise HTTPException(409, "Преподаватель уже существует")
        else:
            # language = await LanguageRepository.create(db, LanguageCreate(lang=schemas.lang))
            teacher = await TeacherRepository.create(db, schemas)
            await TeacherTranslateRepository.create(db, TeacherTranslateCreate(
                name=schemas.name, fullname=schemas.fullname, lang=schemas.lang, teacher_guid=teacher.guid))
        return TeacherOutput(**Teacher.from_orm(teacher).dict())

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> TeacherOutput:
        teacher = await TeacherRepository.get_by_id(db, guid)
        if teacher is None:
            raise HTTPException(404, "Преподаватель не найден")
        return TeacherOutput(**Teacher.from_orm(teacher).dict())

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str, lang: str) -> TeacherOutput:
        teacher = await TeacherRepository.get_by_name(db, name, lang=lang)
        if teacher is None:
            raise HTTPException(404, "Преподаватель не найден")
        return TeacherOutput(**Teacher.from_orm(teacher).dict())

    @staticmethod
    async def get_all(db: AsyncSession) -> list[str]:
        teachers = await TeacherRepository.get_all(db)
        if teachers is None:
            raise HTTPException(404, "Преподаватель не найден")
        return [Teacher.from_orm(teacher).trans.fullname for teacher in teachers]

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: TeacherCreate) -> TeacherOutput:
        teacher = await TeacherRepository.update(db, guid, schemas)
        if teacher is None:
            raise HTTPException(404, "Преподаватель не найден")
        return TeacherOutput(**Teacher.from_orm(teacher).dict())

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await TeacherRepository.delete(db, guid)
        return Response(status_code=204)
