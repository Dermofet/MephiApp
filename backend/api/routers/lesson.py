import uuid
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.config import config
from backend.database.connection import get_session_yield
from backend.schemas.lesson import LessonCreateSchema, LessonOutputSchema, LessonSchema
from backend.services.lesson import LessonService

router = APIRouter(prefix=config.BACKEND_PREFIX)


@router.post(
    "/lessons",
    response_model=LessonOutputSchema,
    response_description="Занятие успешно создано",
    status_code=status.HTTP_201_CREATED,
    description="Создать занятие и вернуть его",
    summary="Создание занятия",
)
async def create(
        schemas: LessonCreateSchema,
        db: AsyncSession = Depends(get_session_yield),
        lesson_service: LessonService = Depends(),
):
    return await lesson_service.create(db=db, schemas=schemas)


@router.get(
    "/lessons/id/{guid}",
    response_model=LessonOutputSchema,
    response_description="Успешный возврат занятия",
    status_code=status.HTTP_200_OK,
    description="Получить занятие по его идентифицирующему номеру",
    summary="Получение занятия по id",
)
async def get(
        guid: str,
        lang: str = "ru",
        db: AsyncSession = Depends(get_session_yield),
        lesson_service: LessonService = Depends(),
):
    return await lesson_service.get(db=db, guid=guid, lang=lang)


@router.get(
    "/lessons",
    response_model=UUID4,
    response_description="Успешный возврат ID занятия",
    status_code=status.HTTP_200_OK,
    description="Получить ID занятия ",
    summary="Получение id занятия",
)
async def get_id(
        schemas: LessonCreateSchema,
        db: AsyncSession = Depends(get_session_yield),
        lesson_service: LessonService = Depends(),
):
    return await lesson_service.get_guid(db=db, schemas=schemas)


@router.get(
    "/lessons/groups/{group}",
    response_model=dict,
    response_description="Успешный возврат занятий",
    status_code=status.HTTP_200_OK,
    description="Получить список занятий определенной группы",
    summary="Получение занятий по группе",
)
async def get_by_group(
        group: str,
        lang: str = "ru",
        db: AsyncSession = Depends(get_session_yield),
        lesson_service: LessonService = Depends(),
):
    return await lesson_service.get_by_group(db=db, group=group, lang=lang)


@router.get(
    "/lessons/teachers",
    response_model=dict,
    response_description="Успешный возврат занятий",
    status_code=status.HTTP_200_OK,
    description="Получить список занятий, где преподает определенный преподаватель",
    summary="Получение занятий по преподавателю",
)
async def get_by_teacher(
        teacher: str,
        lang: str = "ru",
        db: AsyncSession = Depends(get_session_yield),
        lesson_service: LessonService = Depends(),
):
    return await lesson_service.get_by_teacher(db=db, teacher=teacher, lang=lang)


@router.put(
    "/lessons/id/{id}",
    response_model=LessonOutputSchema,
    response_description="Успешное обновление занятия",
    status_code=status.HTTP_200_OK,
    description="Изменить занятие по его id (полное обновление модели)",
    summary="Изменение занятия по id",
)
async def update(
        schemas: LessonCreateSchema,
        guid: UUID4,
        db: AsyncSession = Depends(get_session_yield),
        lesson_service: LessonService = Depends(),
):
    return await lesson_service.update(db=db, guid=guid, schemas=schemas)


@router.put(
    "/lesson-translated/{guid}",
    response_model=LessonOutputSchema,
    response_description="Успешное обновление занятия",
    status_code=status.HTTP_200_OK,
    description="Изменить занятие (добавить новый перевод)",
    summary="Добавить перевод",
)
async def update_translate(
        schemas: LessonCreateSchema,
        guid: UUID4,
        db: AsyncSession = Depends(get_session_yield),
        lesson_service: LessonService = Depends(),
):
    return await lesson_service.update_translate(db=db, schemas=schemas, guid=guid)


@router.delete(
    "/lessons/id/{id}",
    response_description="Успешное удаление занятия",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Удалить занятие по его id",
    summary="Удаление занятия по id",
)
async def delete(
        guid: UUID4,
        db: AsyncSession = Depends(get_session_yield),
        lesson_service: LessonService = Depends(),
):
    return await lesson_service.delete(db=db, guid=guid)
