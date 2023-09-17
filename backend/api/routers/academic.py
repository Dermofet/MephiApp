from fastapi import APIRouter, Depends
# from starlette import status

# from backend.api.schemas.academic import AcademicCreateSchema, AcademicOutputSchema
# from backend.api.services.academic import AcademicService
from config import config

router = APIRouter(prefix=config.BACKEND_PREFIX)

# TODO Удалить

# @router.post(
#     "/academics",
#     response_model=AcademicOutputSchema,
#     response_description="Ученое звание успешно создано",
#     status_code=status.HTTP_201_CREATED,
#     description="Создать ученое звание и вернуть его",
#     summary="Создание ученого звания",
# )
# async def create(
#         schemas: AcademicCreateSchema,
#         academic_service: AcademicService = Depends(AcademicService.get_service),
# ):
#     # academic_service = AcademicService(session=session)
#     return await academic_service.create(schemas=schemas)
