from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.api.database.connection import get_session
from backend.api.routers.utils import get_version
from backend.api.services.utils import get_corps_service
from utils.version import Version

router = APIRouter(prefix="/api/v2.0")


@router.get(
    "/corps",
    response_model=dict[str, list[str]],
    status_code=status.HTTP_200_OK,
    description="Получить корпус",
    summary="Получить корпус",
)
async def get_all(
    version: Version = Depends(get_version),
    session: AsyncSession = Depends(get_session),
):
    corps_service = await get_corps_service(version, session)
    return await corps_service.get_all()
