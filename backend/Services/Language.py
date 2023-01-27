# from fastapi import HTTPException, Response
# from pydantic import UUID4
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from backend.Repositories.Language import LanguageRepository
# from backend.Schemas.Language import LanguageCreate, LanguageOutput
#
#
# class LanguageService:
#     @staticmethod
#     async def create(db: AsyncSession, schemas: LanguageCreate) -> LanguageOutput:
#         language = await LanguageRepository.get_by_name(db, schemas)
#         if language is not None:
#             raise HTTPException(409, "Язык уже существует")
#         else:
#             language = await LanguageRepository.create(db, schemas)
#         return LanguageOutput.from_orm(language)
#
#     @staticmethod
#     async def get(db: AsyncSession, guid: UUID4) -> LanguageOutput:
#         language = await LanguageRepository.get_by_id(db, guid)
#         if language is None:
#             raise HTTPException(404, "Язык не найден")
#         return LanguageOutput.from_orm(language)
#
#     @staticmethod
#     async def get_by_lang(db: AsyncSession, lang: str) -> LanguageOutput:
#         language = await LanguageRepository.get_by_lang(db, lang)
#         if language is None:
#             raise HTTPException(404, "Язык не найден")
#         return LanguageOutput.from_orm(language)
#
#     @staticmethod
#     async def get_all(db: AsyncSession) -> list[str]:
#         languages = await LanguageRepository.get_by_lang(db, lang)
#         if languages is None:
#             raise HTTPException(404, "Язык не найден")
#         return [LanguageOutput.from_orm(language) for language in languages]
#
#     @staticmethod
#     async def update(db: AsyncSession, guid: UUID4, schemas: LanguageCreate) -> LanguageOutput:
#         language = await LanguageRepository.update(db, guid, schemas)
#         if language is None:
#             raise HTTPException(404, "Язык не найден")
#         return LanguageOutput.from_orm(language)
#
#     @staticmethod
#     async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
#         await LanguageRepository.delete(db, guid)
#         return Response(status_code=204)
