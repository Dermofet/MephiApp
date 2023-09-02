from typing import Dict, List

from fastapi import HTTPException, Response
from pydantic import UUID4

from backend.api.schemas.corps import CorpsCreateSchema, CorpsOutputSchema, CorpsSchema
from backend.api.services.base_servise import BaseService


class CorpsService(BaseService):
    async def create(self, schemas: CorpsCreateSchema) -> CorpsOutputSchema:
        corps = await self.facade.get_by_name_corps(schemas.name)
        if corps is not None:
            raise HTTPException(409, "Корпус уже существует")

        corps = await self.facade.create_corps(schemas)
        await self.facade.commit()

        return CorpsOutputSchema(**CorpsSchema.model_validate(corps).model_dump())
    
    async def get(self, guid: UUID4) -> CorpsOutputSchema:
        corps = await self.facade.get_by_id_corps(guid)
        if corps is None:
            raise HTTPException(404, "Корпус не найден")
        return CorpsOutputSchema(**CorpsSchema.model_validate(corps).model_dump())
    
    async def get_by_name(self, name: str) -> CorpsOutputSchema:
        corps = await self.facade.get_by_name_corps(name)
        if corps is None:
            raise HTTPException(404, "Корпус не найден")
        return CorpsOutputSchema(**CorpsSchema.model_validate(corps).model_dump())
    
    async def get_all(self) -> Dict[str, List[str]]:
        corps = await self.facade.get_all_corps()
        corps.sort()
        return {"corps": corps}
    
    async def update(self, guid: UUID4, schemas: CorpsCreateSchema) -> CorpsOutputSchema:
        corps = await self.facade.update_corps(guid, schemas)
        if corps is None:
            raise HTTPException(404, "Корпус не найден")
        await self.facade.commit()
        return CorpsOutputSchema(**CorpsSchema.model_validate(corps).model_dump())

    async def delete(self, guid: UUID4) -> Response:
        await self.facade.delete_corps(guid)
        await self.facade.commit()

        return Response(status_code=204)
