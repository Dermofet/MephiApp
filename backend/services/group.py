from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.academic import AcademicRepository
from backend.repositories.group import GroupRepository
from backend.schemas.academic import AcademicCreateSchema
from backend.schemas.group import GroupCreateSchema, GroupOutputSchema, GroupSchema


class GroupService:
    @staticmethod
    async def create(db: AsyncSession, schemas: GroupCreateSchema) -> GroupOutputSchema:
        group = await GroupRepository.get_by_name(db, schemas.name)
        if group is not None:
            raise HTTPException(409, "Группа уже существует")
        else:
            academic = await AcademicRepository.get_by_name(db, name=schemas.academic)
            if academic is None:
                raise HTTPException(408, "Ученого звание не существует")
            group = await GroupRepository.create(db, schemas, academic_guid=academic.guid)
        return GroupOutputSchema(**GroupSchema.from_orm(group).dict())

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> GroupOutputSchema:
        group = await GroupRepository.get_by_id(db, guid)
        if group is None:
            raise HTTPException(404, "Группа не найдена")
        return GroupOutputSchema(**GroupSchema.from_orm(group).dict())

    @staticmethod
    async def get_all(db: AsyncSession) -> dict[str, list[str]]:
        groups = await GroupRepository.get_all(db)
        res = [GroupSchema.from_orm(group).name for group in groups]
        res.sort()
        return {"groups": res}

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> GroupOutputSchema:
        group = await GroupRepository.get_by_name(db, name)
        if group is None:
            raise HTTPException(404, "Группа не найдена")
        return GroupOutputSchema(**GroupSchema.from_orm(group).dict())

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: GroupCreateSchema) -> GroupOutputSchema:
        group = await GroupRepository.update(db, guid, schemas)
        if group is None:
            raise HTTPException(404, "Группа не найдена")
        return GroupOutputSchema(**GroupSchema.from_orm(group).dict())

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await GroupRepository.delete(db, guid)
        return Response(status_code=204)
