from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.database.connection import get_session
from backend.api.database.facade import FacadeDB, IFacadeDB


class BaseService:
    facade: IFacadeDB

    def __init__(self, session: AsyncSession):
        self.facade = FacadeDB(session)

    @classmethod
    def get_service(cls, session: AsyncSession = Depends(get_session)):
        return cls(session)
