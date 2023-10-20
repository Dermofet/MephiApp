from typing import Dict, List

from fastapi import HTTPException, Response
from pydantic import UUID4

from backend.api.schemas.teacher import TeacherCreateSchema, TeacherOutputSchema, TeacherSchema
from backend.api.services.base_servise import BaseService


class TeacherService(BaseService):
    async def create(self, schemas: TeacherCreateSchema) -> TeacherOutputSchema:
        teacher = await self.facade.get_by_name_teacher(schemas.name)
        if teacher is not None:
            raise HTTPException(409, "Преподаватель уже существует")

        teacher = await self.facade.create_teacher(schemas)
        await self.facade.commit()
        return TeacherOutputSchema(**TeacherSchema.model_validate(teacher).model_dump())

    async def get(self, guid: UUID4) -> TeacherOutputSchema:
        teacher = await self.facade.get_by_id_teacher(guid)
        if teacher is None:
            raise HTTPException(404, "Преподаватель не найден")
        return TeacherOutputSchema(**TeacherSchema.model_validate(teacher).model_dump())

    async def get_by_name(self, name: str, lang: str) -> TeacherOutputSchema:
        lang = "ru" if lang == "ru" else "en"
        teacher = await self.facade.get_by_name_teacher(name)

        if teacher is None:
            raise HTTPException(404, "Преподаватель не найден")

        trans = await self.facade.get_trans_teacher(teacher, lang)
        return TeacherOutputSchema(
            url=teacher.url, alt_url=teacher.alt_url, lang=trans.lang, name=trans.name, fullname=trans.fullname
        )

    async def get_all(self, lang: str) -> Dict[str, List[str]]:
        lang = "ru" if lang == "ru" else "en"
        teachers = await self.facade.get_all_teacher(lang)
        teachers.sort()
        return {"teachers": teachers}

    async def update(self, guid: UUID4, schemas: TeacherCreateSchema) -> TeacherOutputSchema:
        teacher = await self.facade.update_teacher(guid, schemas)
        if teacher is None:
            raise HTTPException(404, "Преподаватель не найден")
        await self.facade.commit()
        return TeacherOutputSchema(**TeacherSchema.model_validate(teacher).model_dump())

    async def delete(self, guid: UUID4) -> Response(status_code=204):
        await self.facade.delete_teacher(guid)
        await self.facade.commit()
        return Response(status_code=204)
