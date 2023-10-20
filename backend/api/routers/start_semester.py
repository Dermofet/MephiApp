from fastapi import APIRouter, Depends
from starlette import status

from backend.api.schemas.start_semester import StartSemesterCreateSchema, StartSemesterOutputSchema
from backend.api.services.start_semester import StartSemesterService
from config import config

router = APIRouter(prefix=config.BACKEND_PREFIX)


# @router.post(
#     "/start_semester",
#     response_model=StartSemesterOutputSchema,
#     response_description="Дата успешно создана",
#     status_code=status.HTTP_201_CREATED,
#     description="Создать дату начала семестра и вернуть ее",
#     summary="Создание даты",
# )
# async def create(
#         schemas: StartSemesterCreateSchema,
#         start_semester_service: StartSemesterService = Depends(StartSemesterService.get_service)
# ):
#     return await start_semester_service.create(schemas=schemas)


@router.get(
    "/start_semester",
    response_model=StartSemesterOutputSchema,
    status_code=status.HTTP_200_OK,
    description="Получить дату начала семестра",
    summary="Получить дату",
)
async def get(start_semester_service: StartSemesterService = Depends(StartSemesterService.get_service)):
    return await start_semester_service.get()


# TODO Удалить

# @router.put(
#     "/start_semester",
#     response_model=StartSemesterOutputSchema,
#     status_code=status.HTTP_200_OK,
#     description="Получить дату начала семестра",
#     summary="Получить дату",
# )
# async def update(
#         schema: StartSemesterCreateSchema,
#         start_semester_service: StartSemesterService = Depends(StartSemesterService.get_service)
# ):
#     return await start_semester_service.update(schema)
