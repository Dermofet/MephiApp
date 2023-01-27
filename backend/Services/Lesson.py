from typing import List

from fastapi import HTTPException, Response
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from backend.DataBase.Models.Lesson import Lesson as LessonModel
from backend.Repositories.Academic import AcademicRepository
from backend.Repositories.Group import GroupRepository
from backend.Repositories.Lesson import LessonRepository
from backend.Repositories.LessonTranslate import LessonTranslateRepository
from backend.Repositories.Room import RoomRepository
from backend.Repositories.Teacher import TeacherRepository
from backend.Repositories.TeacherTranslate import TeacherTranslateRepository
from backend.Schemas.Academic import AcademicCreate
from backend.Schemas.Group import GroupCreate
from backend.Schemas.Lesson import Lesson, LessonCreate, LessonOutput
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
            lesson = await LessonService.__create_all_by_lesson__(db, schemas)
        return LessonOutput(**Lesson.from_orm(lesson).dict())

    @staticmethod
    async def __create_all_by_lesson__(db: AsyncSession, schemas: LessonCreate) -> LessonModel:
        # Room
        room = await RoomRepository.get_by_number(db, schemas.room)
        if room is None:
            await RoomRepository.create(db, RoomCreate(number=schemas.room))

        # Academic
        academic = await AcademicRepository.get_by_name(db, schemas.academic)
        if academic is None:
            academic = await AcademicRepository.create(db, AcademicCreate(name=schemas.academic))

        # Group
        group = await GroupRepository.get_by_name(db, schemas.group)
        if group is None:
            await GroupRepository.create(db, GroupCreate(name=schemas.group,
                                                         course=schemas.course,
                                                         academic=schemas.academic), academic_guid=academic.guid)

        # Teacher
        teacher = await TeacherRepository.get_by_name(db, schemas.teacher_name, lang=schemas.lang)
        if teacher is None:
            teacher = await TeacherRepository.create(
                db,
                TeacherCreate(online_url="",
                              alt_online_url="",
                              name=schemas.teacher_name,
                              fullname="",
                              lang=schemas.lang)
            )

            # LessonTeacher
            await TeacherTranslateRepository.create(
                db,
                TeacherTranslateCreate(name=schemas.teacher_name,
                                       fullname="",
                                       lang=schemas.lang,
                                       teacher_guid=teacher.guid)
            )

        # Lesson
        lesson = await LessonRepository.create(db, schemas)
        await LessonTranslateRepository.create(db,
                                               LessonTranslateCreate(type=schemas.type,
                                                                     name=schemas.name,
                                                                     subgroup=schemas.subgroup,
                                                                     lesson_guid=lesson.guid,
                                                                     lang=schemas.lang)
                                               )

        return lesson

    @staticmethod
    async def get(db: AsyncSession, guid: UUID4, lang: str) -> LessonOutput:
        lesson = await LessonRepository.get_by_id(db, guid, lang)
        if lesson is None:
            raise HTTPException(404, "Занятие не найдено")
        return LessonOutput(**Lesson.from_orm(lesson).dict())

    @staticmethod
    async def get_by_group(db: AsyncSession, group: str, lang: str) -> list[LessonOutput]:
        lessons = await LessonRepository.get_by_group(db, group, lang)
        if len(lessons) == 0:
            raise HTTPException(404, "Занятие не найдено")
        results = [Lesson.from_orm(lesson) for lesson in lessons]
        return [LessonOutput(**result.dict()) for result in results]

    @staticmethod
    async def get_by_teacher(db: AsyncSession, teacher: str, lang: str) -> list[LessonOutput]:
        lessons = await LessonRepository.get_by_teacher(db, teacher, lang)
        if lessons is None:
            raise HTTPException(404, "Занятие не найдено")
        results = [Lesson.from_orm(lesson) for lesson in lessons]
        return [LessonOutput(**result.dict()) for result in results]

    @staticmethod
    async def update(db: AsyncSession, guid: UUID4, schemas: LessonCreate) -> LessonOutput:
        lesson = await LessonRepository.update(db, guid, schemas)
        if lesson is None:
            raise HTTPException(404, "Занятие не найдено")
        result = Lesson.from_orm(lesson)
        return LessonOutput(**result.dict())

    @staticmethod
    async def delete(db: AsyncSession, guid: UUID4) -> Response(status_code=204):
        await LessonRepository.delete(db, guid)
        return Response(status_code=204)
