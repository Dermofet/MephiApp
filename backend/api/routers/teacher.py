from fastapi import APIRouter, Depends
from pydantic import UUID4
from starlette import status

from backend.api.schemas.teacher import TeacherCreateSchema, TeacherOutputSchema
from backend.api.services.teacher import TeacherService
from config import config

router = APIRouter(prefix=config.BACKEND_PREFIX)

# TODO Удалить

# @router.post(
#     "/teachers",
#     response_model=TeacherOutputSchema,
#     response_description="Преподаватель успешно создан",
#     status_code=status.HTTP_201_CREATED,
#     description="Создать преподавателя и вернуть его",
#     summary="Создание преподавателя",
# )
# async def create(
#         schemas: TeacherCreateSchema,
#         teacher_service: TeacherService = Depends(TeacherService.get_service),
# ):
#     return await teacher_service.create(schemas=schemas)


@router.get(
    "/teachers/{lang}",
    response_model=dict[str, list[str]],
    status_code=status.HTTP_200_OK,
    description="Получить полные ФИО всеx преподавателей",
    summary="Получить всех преподавателей",
)
async def get_all(
        lang: str = "ru",
        teacher_service: TeacherService = Depends(TeacherService.get_service),
):
    return await teacher_service.get_all(lang)


@router.get(
    "/teachers/{name}",
    response_model=TeacherOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Получить полное ФИО преподавателя",
    summary="Получить ФИО преподавателя",
)
async def get_by_name(
        name: str,
        lang: str = "ru",
        teacher_service: TeacherService = Depends(TeacherService.get_service),
):
    return await teacher_service.get_by_name(name=name, lang=lang)


# @router.put(
#     "/teachers/{guid}",
#     response_model=TeacherOutputSchema,
#     status_code=status.HTTP_200_OK,
#     description="Обновить информацию о преподавателе по id",
#     summary="Обновить информацию о преподавателе по id",
# )
# async def update(
#         schemas: TeacherCreateSchema,
#         guid: UUID4,
#         teacher_service: TeacherService = Depends(TeacherService.get_service),
# ):
#     return await teacher_service.update(guid, schemas)


# @router.put(
#     "/teachers",
#     response_model=TeacherOutputSchema,
#     status_code=status.HTTP_200_OK,
#     description="Обновить информацию о преподавателе",
#     summary="Обновить информацию о преподавателе",
# )
# async def update(
#         schemas: TeacherCreateSchema,
#         teacher_service: TeacherService = Depends(TeacherService.get_service),
# ):
#     return await teacher_service.update(db, schemas)
