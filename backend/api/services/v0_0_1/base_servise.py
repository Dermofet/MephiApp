from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.database.connection import get_session
from backend.api.database.facade import FacadeDB, IFacadeDB
from utils.version import Version


class BaseService:
    facade: IFacadeDB

    def __init__(self, session: AsyncSession, version: Version):
        self.facade = FacadeDB(session, version)

    @classmethod
    def get_service(cls, version: Version, session: AsyncSession = Depends(get_session)):
        return cls(session, version)
