from fastapi import APIRouter, Body, Depends
from pydantic import UUID4
from starlette import status

from backend.api.schemas.lesson import LessonCreateSchema, LessonOutputSchema
from backend.api.services.lesson import LessonService
from config import config

router = APIRouter(prefix=config.BACKEND_PREFIX)

# TODO Удалить

# @router.post(
#     "/lessons",
#     response_model=LessonOutputSchema,
#     response_description="Занятие успешно создано",
#     status_code=status.HTTP_201_CREATED,
#     description="Создать занятие и вернуть его",
#     summary="Создание занятия",
# )
# async def create(
#         schemas: LessonCreateSchema = Body(..., description="Тело запроса"),
#         lesson_service: LessonService = Depends(LessonService.get_service),
# ):
#     return await lesson_service.create(schemas=schemas)


# @router.get(
#     "/lessons/id/{guid}",
#     response_model=LessonOutputSchema,
#     response_description="Успешный возврат занятия",
#     status_code=status.HTTP_200_OK,
#     description="Получить занятие по его идентифицирующему номеру",
#     summary="Получение занятия по id",
# )
# async def get(
#         guid: str,
#         lang: str = "ru",
#         lesson_service: LessonService = Depends(LessonService.get_service),
# ):
#     return await lesson_service.get(guid=guid, lang=lang)

# @router.get(
#     "/lessons",
#     response_model=UUID4,
#     response_description="Успешный возврат ID занятия",
#     status_code=status.HTTP_200_OK,
#     description="Получить ID занятия ",
#     summary="Получение id занятия",
# )
# async def get_id(
#         schemas: LessonCreateSchema,
#         lesson_service: LessonService = Depends(LessonService.get_service),
# ):
#     return await lesson_service.get_guid(schemas=schemas)


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
        lesson_service: LessonService = Depends(LessonService.get_service),
):
    return await lesson_service.get_by_group(group=group, lang=lang)


@router.get(
    "/lessons/teachers/{teacher}",
    response_model=dict,
    response_description="Успешный возврат занятий",
    status_code=status.HTTP_200_OK,
    description="Получить список занятий, где преподает определенный преподаватель",
    summary="Получение занятий по преподавателю",
)
async def get_by_teacher(
        teacher: str,
        lang: str = "ru",
        lesson_service: LessonService = Depends(LessonService.get_service),
):
    return await lesson_service.get_by_teacher(teacher=teacher, lang=lang)


# @router.put(
#     "/lessons/id/{id}",
#     response_model=LessonOutputSchema,
#     response_description="Успешное обновление занятия",
#     status_code=status.HTTP_200_OK,
#     description="Изменить занятие по его id (полное обновление модели)",
#     summary="Изменение занятия по id",
# )
# async def update(
#         guid: UUID4,
#         schemas: LessonCreateSchema = Body(..., description="Тело запроса"),
#         lesson_service: LessonService = Depends(LessonService.get_service),
# ):
#     return await lesson_service.update(guid=guid, schemas=schemas)


# @router.put(
#     "/lesson-translated/{guid}",
#     response_model=LessonOutputSchema,
#     response_description="Успешное обновление занятия",
#     status_code=status.HTTP_200_OK,
#     description="Изменить занятие (добавить новый перевод)",
#     summary="Добавить перевод",
# )
# async def update_translate(
#         guid: UUID4,
#         schemas: LessonCreateSchema = Body(..., description="Тело запроса"),
#         lesson_service: LessonService = Depends(LessonService.get_service),
# ):
#     return await lesson_service.update_translate(schemas=schemas, guid=guid)


# @router.delete(
#     "/lessons/id/{id}",
#     response_description="Успешное удаление занятия",
#     status_code=status.HTTP_204_NO_CONTENT,
#     description="Удалить занятие по его id",
#     summary="Удаление занятия по id",
# )
# async def delete(
#         guid: UUID4,
#         lesson_service: LessonService = Depends(LessonService.get_service),
# ):
#     return await lesson_service.delete(guid=guid)
