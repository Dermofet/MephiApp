from typing import List

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.DataBase.Models.Group import Group
from backend.Repositories.Academic import AcademicRepository
from backend.Schemas.Academic import AcademicCreate
from backend.Schemas.Group import GroupCreate, GroupOutput


class GroupRepository:
    @staticmethod
    async def create(db: AsyncSession, schemas: GroupCreate, academic_guid: UUID4) -> Group:
        group = Group(name=schemas.name, course=schemas.course, academic_guid=academic_guid)
        db.add(group)
        await db.commit()
        await db.refresh(group)
        return group

    @staticmethod
    async def get_by_id(db: AsyncSession, guid: UUID4) -> Group:
        group = await db.execute(select(Group).where(Group.guid == guid).limit(1))
        return group.scalar()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Group]:
        groups = await db.execute(select(Group))
        return groups.scalars().unique().all()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Group:
        group = await db.execute(select(Group).where(Group.name == name).limit(1))
        return group.scalar()

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: GroupCreate) -> Group:
        group = await GroupRepository.get_by_id(db, guid)

        if group is None:
            HTTPException(status_code=404, detail="Группа не найдена")

        group = await db.execute(update(Group).where(Group.guid == guid).values(**schemas.dict()))
        await db.commit()
        await db.refresh(group)
        return group

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> None:
        await db.execute(delete(Group).where(Group.guid == guid))
        await db.commit()
