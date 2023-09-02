from fastapi import HTTPException, Response
from pydantic import UUID4

from backend.api.schemas.academic import AcademicCreateSchema, AcademicOutputSchema, AcademicSchema
from backend.api.services.base_servise import BaseService


class AcademicService(BaseService):
    async def create(self, schemas: AcademicCreateSchema) -> AcademicOutputSchema:
        academic = await self.facade.get_by_name_academic(schemas.name)
        if academic is not None:
            raise HTTPException(409, "Ученое звание уже существует")
        academic = await self.facade.create_academic(schemas)
        await self.facade.commit()
        return AcademicOutputSchema(**AcademicSchema.model_validate(academic).model_dump())

    async def get(self, guid: UUID4) -> AcademicOutputSchema:
        academic = await self.facade.get_by_id_academic(guid)
        if academic is None:
            raise HTTPException(404, "Ученое звание не найдено")
        return AcademicOutputSchema(**AcademicSchema.model_validate(academic).model_dump())
    
    async def get_by_name(self, name: str) -> AcademicOutputSchema:
        academic = await self.facade.get_by_name_academic(name)
        if academic is None:
            raise HTTPException(404, "Ученое звание не найдено")
        return AcademicOutputSchema(**AcademicSchema.model_validate(academic).model_dump())
    
    async def update(self, guid: UUID4, schemas: AcademicCreateSchema) -> AcademicOutputSchema:
        academic = await self.facade.update_academic(guid, schemas)
        if academic is None:
            raise HTTPException(404, "Ученое звание не найдено")

        await self.facade.commit()
        return AcademicOutputSchema(**AcademicSchema.model_validate(academic).model_dump())
    
    async def delete(self, guid: UUID4) -> Response:
        await self.facade.delete_academic(guid)
        await self.facade.commit()

        return Response(status_code=204)
