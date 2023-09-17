from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.database.models.start_semester import StartSemesterModel
from backend.api.schemas.start_semester import StartSemesterCreateSchema

class StartSemesterDAO:
    """
    DAO для работы с начальным семестром
    """
    _session: AsyncSession

    def __init__(self, session: AsyncSession):
        self._session = session

    """
    Создание начального семестра
    """
    async def create(self, data: StartSemesterCreateSchema) -> StartSemesterModel:
        start_semester = StartSemesterModel(**data.model_dump())

        self._session.add(start_semester)
        await self._session.flush()
        await self._session.refresh(start_semester)

        return start_semester

    """
    Получение начального семестра
    """
    async def get(self) -> StartSemesterModel:
        start_semester = await self._session.execute(select(StartSemesterModel).limit(1))
        return start_semester.scalar()

    """
    Обновление начального семестра
    """
    async def update(self, data: StartSemesterCreateSchema) -> StartSemesterModel:
        start_semester = await self.get()

        if start_semester is None:
            raise HTTPException(404, "Даты не существует")

        await self._session.execute(
            update(StartSemesterModel)
            .where(StartSemesterModel.guid == start_semester.guid)
            .values(**data.model_dump())
        )
        await self._session.flush()
        await self._session.refresh(start_semester)
        return start_semester
