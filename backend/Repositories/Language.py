# from typing import List
#
# from fastapi import HTTPException
# from pydantic import UUID4
# from sqlalchemy import delete, select, update
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from backend.DataBase.Models.Language import Language
# from backend.Schemas.Language import LanguageCreate, LanguageOutput
#
#
# class LanguageRepository:
#     @staticmethod
#     async def create(db: AsyncSession, schemas: LanguageCreate) -> Language:
#         lang = Language(**schemas.dict(exclude_unset=True))
#         db.add(lang)
#         await db.commit()
#         await db.refresh(lang)
#         return lang
#
#     @staticmethod
#     async def get_by_id(db: AsyncSession, guid: UUID4) -> Language:
#         lang = await db.execute(select(Language).where(Language.guid == guid).limit(1))
#         return lang.scalars().all()[0] if lang.scalars().all()[0] else None
#
#     @staticmethod
#     async def get_all(db: AsyncSession) -> List[Language]:
#         langs = await db.execute(select(Language))
#         return langs.scalars().unique().all() if langs.scalars().unique().all() else None
#
#     @staticmethod
#     async def get_by_lang(db: AsyncSession, lang: str) -> Language:
#         lang = await db.execute(select(Language).where(Language.lang == lang).limit(1))
#         return lang.scalars().all()[0] if lang.scalars().all() else None
#
#     @staticmethod
#     async def update(db: AsyncSession, guid: UUID4, schemas: LanguageCreate) -> Language:
#         lang = await LanguageRepository.get_by_id(db, guid)
#
#         if lang is None:
#             HTTPException(status_code=404, detail="Язык не найден")
#
#         lang = await db.execute(update(Language).where(Language.guid == guid).values(**schemas.dict()))
#         await db.commit()
#         await db.refresh(lang)
#         return lang
#
#     @staticmethod
#     async def delete(db: AsyncSession, guid: UUID4) -> None:
#         await db.execute(delete(Language).where(Language.guid == guid))
#         await db.commit()
