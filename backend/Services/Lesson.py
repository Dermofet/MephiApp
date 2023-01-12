from typing import List

from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.Repositories.Academic import AcademicRepository
from backend.Repositories.Group import GroupRepository
from backend.Repositories.Language import LanguageRepository
from backend.Repositories.Lesson import LessonRepository
from backend.Repositories.LessonTranslate import LessonTranslateRepository
from backend.Repositories.Room import RoomRepository
from backend.Repositories.Teacher import TeacherRepository
from backend.Repositories.TeacherTranslate import TeacherTranslateRepository
from backend.Schemas.Academic import AcademicCreate
from backend.Schemas.Group import GroupCreate
from backend.Schemas.Language import LanguageCreate
from backend.Schemas.Lesson import LessonCreate, LessonOutput, LessonOutputFromDB
from backend.Schemas.LessonTranslate import LessonTranslateCreate
from backend.Schemas.Room import RoomCreate
from backend.Schemas.Teacher import TeacherCreate
from backend.Schemas.TeacherTranslate import TeacherTranslateCreate


class LessonService:
    @staticmethod
    async def create(db: AsyncSession, schemas: LessonCreate) -> LessonOutput:
        lesson = await LessonRepository.get_unique(db, schemas)
        if lesson is not None:
            raise HTTPException(409, "Занятие уже существует")
        else:
            room = await RoomRepository.get_by_number(db, schemas.room)
            if room is None:
                room = await RoomRepository.create(
                    db,
                    RoomCreate(number=schemas.room)
                )

            ######################################################################

            academic = await AcademicRepository.get_by_name(db, schemas.academic)
            if academic is None:
                academic = await AcademicRepository.create(
                    db,
                    AcademicCreate(name=schemas.academic)
                )

            ######################################################################

            group = await GroupRepository.get_by_name(db, schemas.group)
            if group is None:
                group = await GroupRepository.create(
                    db,
                    GroupCreate(name=schemas.group, course=schemas.course),
                    academic_guid=academic.guid
                )

            ######################################################################

            language = await LanguageRepository.get_by_lang(db, schemas.lang)
            if language is None:
                language = await LanguageRepository.create(
                    db,
                    LanguageCreate(lang=schemas.lang)
                )

            ######################################################################

            teacher = await TeacherRepository.get_by_name(db, schemas.teacher_name)
            if teacher is None:
                teacher_translate = await TeacherTranslateRepository.create(
                    db,
                    TeacherTranslateCreate(name=schemas.teacher_name, fullname=""),
                    lang_guid=language.guid
                )
                teacher = await TeacherRepository.create(
                    db,
                    TeacherCreate(online_url="", alt_online_url=""),
                    trans_guid=teacher_translate.guid
                )

            ######################################################################

            lesson_translate = await LessonTranslateRepository.create(
                db,
                LessonTranslateCreate(type=schemas.type, name=schemas.name, subgroup=schemas.subgroup)
            )
            lesson = await LessonRepository.create(
                db,
                schemas,
                room_guid=room.guid,
                group_guid=group.guid,
                teacher_guid=teacher.guid,
                lesson_translate_guid=lesson_translate.guid
            )

            ######################################################################

            result = LessonOutputFromDB.from_orm(lesson)
            if lesson.weeks == 0:
                result.weeks = [x for x in range(2, 16, 2)]
            elif lesson.weeks == 1:
                result.weeks = [x for x in range(1, 15, 2)]
            else:
                result.weeks = [x for x in range(1, 16)]
            print(result)
        return LessonOutput(**result.dict())

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4) -> LessonOutput:
        lesson = await LessonRepository.get_by_id(db, guid)
        if lesson is None:
            raise HTTPException(404, "Занятие не найдено")
        return LessonOutput.from_orm(lesson)

    @staticmethod
    async def get_by_group(db: AsyncSession, group: str) -> list[LessonOutput]:
        lessons = await LessonRepository.get_by_group(db, group)
        if lessons is None:
            raise HTTPException(404, "Занятие не найдено")
        return [LessonOutput.from_orm(lesson) for lesson in lessons]

    @staticmethod
    async def get_by_teacher(db: AsyncSession, teacher: str) -> list[LessonOutput]:
        lessons = await LessonRepository.get_by_teacher(db, teacher)
        if lessons is None:
            raise HTTPException(404, "Занятие не найдено")
        return [LessonOutput.from_orm(lesson) for lesson in lessons]

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: LessonCreate) -> LessonOutput:
        lesson = await LessonRepository.update(db, guid, schemas)
        if lesson is None:
            raise HTTPException(404, "Занятие не найдено")
        return LessonOutput.from_orm(lesson)

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await LessonRepository.delete(db, guid)
        return Response(status_code=204)
