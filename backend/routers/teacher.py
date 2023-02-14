from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.config import config
from backend.database.connection import get_session
from backend.schemas.teacher import TeacherCreateSchema, TeacherOutputSchema
from backend.schemas.teacher_translate import TeacherTranslateOutputSchema
from backend.services.teacher import TeacherService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.post(
    "/teacher",
    response_model=TeacherTranslateOutputSchema,
    response_description="Преподаватель успешно создан",
    status_code=status.HTTP_201_CREATED,
    description="Создать преподавателя и вернуть его",
    summary="Создание преподавателя",
)
async def create(
        schemas: TeacherCreateSchema,
        db: AsyncSession = Depends(get_session),
        teacher_service: TeacherService = Depends(),
):
    return await teacher_service.create(db=db, schemas=schemas)


@router.get(
    "/teachers/{lang}",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
    description="Получить полные ФИО всеx преподавателей",
    summary="Получить всех преподавателей",
)
async def get_all(
        lang: str,
        db: AsyncSession = Depends(get_session),
        teacher_service: TeacherService = Depends(),
):
    return await teacher_service.get_all(db, lang)


@router.put(
    "/teacher/{guid}",
    response_model=TeacherTranslateOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Обновить информацию о преподавателе по id",
    summary="Обновить информацию о преподавателе по id",
)
async def update(
        guid,
        schemas: TeacherCreateSchema,
        db: AsyncSession = Depends(get_session),
        teacher_service: TeacherService = Depends(),
):
    return await teacher_service.update_by_id(db, guid, schemas)


@router.put(
    "/teacher",
    response_model=TeacherTranslateOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Обновить информацию о преподавателе",
    summary="Обновить информацию о преподавателе",
)
async def update(
        schemas: TeacherCreateSchema,
        db: AsyncSession = Depends(get_session),
        teacher_service: TeacherService = Depends(),
):
    return await teacher_service.update(db, schemas)
