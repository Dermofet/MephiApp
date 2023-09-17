from typing import Dict, List

from fastapi import HTTPException, Response
from pydantic import UUID4

from backend.api.schemas.group import GroupCreateSchema, GroupOutputSchema, GroupSchema
from backend.api.services.base_servise import BaseService


class GroupService(BaseService):
    async def create(self, schemas: GroupCreateSchema) -> GroupOutputSchema:
        group = await self.facade.get_by_name_group(schemas.name)
        if group is not None:
            raise HTTPException(409, "Группа уже существует")

        academic = await self.facade.get_by_name_academic(name=schemas.academic)
        if academic is None:
            raise HTTPException(408, "Ученого звание не существует")

        group = await self.facade.create_group(schemas, academic_guid=academic.guid)
        await self.facade.commit()

        return GroupOutputSchema(**GroupSchema.model_validate(group).model_dump())

    async def get(self, guid: UUID4) -> GroupOutputSchema:
        group = await self.facade.get_by_id_group(guid)
        if group is None:
            raise HTTPException(404, "Группа не найдена")
        return GroupOutputSchema(**GroupSchema.model_validate(group).model_dump())

    
    async def get_all(self) -> Dict[str, List[str]]:
        groups = await self.facade.get_all_group()
        groups.sort()
        return {"groups": groups}

    
    async def get_by_name(self, name: str) -> GroupOutputSchema:
        group = await self.facade.get_by_name_group(name)
        if group is None:
            raise HTTPException(404, "Группа не найдена")
        
        return GroupOutputSchema(
            **GroupSchema(
                guid=group.guid,
                name=group.name,
                course=group.course,
                academic=await self.facade.get_academic_group(group)
            ).model_dump()
        )

    
    async def update(self, guid: UUID4, schemas: GroupCreateSchema) -> GroupOutputSchema:
        group = await self.facade.update_group(guid, schemas)
        if group is None:
            raise HTTPException(404, "Группа не найдена")
        await self.facade.commit()
        return GroupOutputSchema(**GroupSchema.model_validate(group).model_dump())

    
    async def delete(self, guid: UUID4) -> Response:
        await self.facade.delete_group(guid)
        await self.facade.commit()

        return Response(status_code=204)
