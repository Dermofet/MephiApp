from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.Repositories.Academic import AcademicRepository
from backend.Repositories.Group import GroupRepository
from backend.Schemas.Academic import AcademicCreate
from backend.Schemas.Group import GroupCreate, GroupOutput


class GroupService:
    @staticmethod
    async def create(db: AsyncSession, schemas: GroupCreate) -> GroupOutput:
        group = await GroupRepository.get_by_name(db, schemas)
        if group is not None:
            raise HTTPException(409, "Группа уже существует")
        else:
            academic = await AcademicRepository.create(db, AcademicCreate(name=schemas.academic))
            group = await GroupRepository.create(db, schemas, academic_guid=academic.guid)
        return GroupOutput.from_orm(group)

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> GroupOutput:
        group = await GroupRepository.get_by_id(db, guid)
        if group is None:
            raise HTTPException(404, "Группа не найдена")
        return GroupOutput.from_orm(group)

    @staticmethod
    async def get_all(db: AsyncSession) -> list[str]:
        groups = await GroupRepository.get_all(db)
        if groups is None:
            raise HTTPException(404, "Группа не найдена")
        return [GroupOutput.from_orm(group).name for group in groups]

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> GroupOutput:
        group = await GroupRepository.get_by_name(db, name)
        if group is None:
            raise HTTPException(404, "Группа не найдена")
        return GroupOutput.from_orm(group)

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: GroupCreate) -> GroupOutput:
        group = await GroupRepository.update(db, guid, schemas)
        if group is None:
            raise HTTPException(404, "Группа не найдена")
        return GroupOutput.from_orm(group)

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await GroupRepository.delete(db, guid)
        return Response(status_code=204)
