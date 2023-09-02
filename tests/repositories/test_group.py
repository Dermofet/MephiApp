from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.group import GroupModel
from backend.schemas.group import GroupCreateSchema


class GroupRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: GroupCreateSchema, academic_guid: UUID4) -> GroupModel:
        group = GroupModel(name=schemas.name, course=schemas.course, academic_guid=academic_guid)
        db.add(group)
        await db.commit()
        await db.refresh(group)
        return group

    @staticmethod
    async def bulk_insert(db: AsyncSession, data: list) -> None:
        await db.execute(insert(GroupModel).values(data))

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> GroupModel:
        group = await db.execute(select(GroupModel).where(GroupModel.guid == guid).limit(1))
        return group.scalar()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[str]:
        groups = await db.execute(select(GroupModel.name))
        return groups.scalars().unique().all()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> GroupModel:
        group = await db.execute(select(GroupModel).where(GroupModel.name == name).limit(1))
        return group.scalar()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: GroupCreateSchema) -> GroupModel:
        group = await GroupRepository.get_by_id(db, guid)

        if group is None:
            HTTPException(status_code=404, detail="Группа не найдена")

        group = await db.execute(update(GroupModel).where(GroupModel.guid == guid).values(**schemas.dict()))
        await db.commit()
        await db.refresh(group)
        return group

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(GroupModel).where(GroupModel.guid == guid))
        await db.commit()
