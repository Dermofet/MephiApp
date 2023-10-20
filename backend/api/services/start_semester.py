from fastapi import HTTPException

from backend.api.schemas.start_semester import StartSemesterCreateSchema, StartSemesterOutputSchema, StartSemesterSchema
from backend.api.services.base_servise import BaseService


class StartSemesterService(BaseService):
    async def create(self, schemas: StartSemesterCreateSchema) -> StartSemesterOutputSchema:
        start_semester = await self.facade.get_start_semester()
        if start_semester is not None:
            raise HTTPException(409, "Дата уже существует")

        start_semester = await self.facade.create_start_semester(schemas)
        await self.facade.commit()
        return StartSemesterOutputSchema(**StartSemesterSchema.model_validate(start_semester).model_dump())

    async def get(self) -> StartSemesterOutputSchema:
        start_semester = await self.facade.get_start_semester()
        if start_semester is None:
            raise HTTPException(404, "Даты не cуществует")
        return StartSemesterOutputSchema(**StartSemesterSchema.model_validate(start_semester).model_dump())

    async def update(self, schemas: StartSemesterCreateSchema) -> StartSemesterOutputSchema:
        start_semester = await self.facade.update_start_semester(schemas)
        if start_semester is None:
            raise HTTPException(404, "Даты не cуществует")
        await self.facade.commit()
        return StartSemesterOutputSchema(**StartSemesterSchema.model_validate(start_semester).model_dump())
