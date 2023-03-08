from backend.database.connection import get_session
from backend.repositories.academic import AcademicRepository
from backend.repositories.corps import CorpsRepository
from backend.repositories.group import GroupRepository
from backend.repositories.lesson import LessonRepository
from backend.repositories.room import RoomRepository
from backend.repositories.teacher import TeacherRepository
from backend.schemas.academic import AcademicCreateSchema
from backend.schemas.corps import CorpsCreateSchema
from backend.schemas.group import GroupCreateSchema
from backend.schemas.lesson import LessonCreateSchema
from backend.schemas.room import RoomCreateSchema
from backend.schemas.teacher import TeacherCreateSchema

from .connection import celery


class Worker:
    # Academic create
    @staticmethod
    @celery.task
    async def academic_create(schemas: AcademicCreateSchema) -> AcademicModel:
        async with get_session() as db:
            academic = AcademicRepository.get_by_name(db, schemas.name)

            if academic is not None:
                raise HTTPException(409, "Ученое звание уже существует")

            academic = AcademicModel(**schemas.dict())
            db.add(academic)
            await db.commit()
            await db.refresh(academic)
        return academic

    # Corps create
    @staticmethod
    @celery.task
    async def corps_create(schemas: CorpsCreateSchema) -> CorpsModel:
        async with get_session() as db:
            corps = await CorpsRepository.get_by_name(db, schemas.name)

            if corps is not None:
                raise HTTPException(409, "Корпус уже существует")

            corps = CorpsModel(**schemas.dict())
            db.add(corps)
            await db.commit()
            await db.refresh(corps)
        return corps

    # Group create
    @staticmethod
    @celery.task
    async def group_create(schemas: GroupCreateSchema, academic_guid: UUID4) -> GroupModel:
        async with get_session() as db:
            group = await GroupRepository.get_by_name(db, schemas.name)

            if group is not None:
                raise HTTPException(409, "Группа уже существует")

            group = GroupModel(name=schemas.name, course=schemas.course, academic_guid=academic_guid)
            db.add(group)
            await db.commit()
            await db.refresh(group)
        return group

    # Room create
    @staticmethod
    @celery.task
    async def room_create(schemas: RoomCreateSchema, corps_guid) -> RoomModel:
        async with get_session() as db:
            room = await RoomRepository.get_by_number(db, schemas.number)

            if room is not None:
                raise HTTPException(409, "Аудитория уже существует")

            room = RoomModel(number=schemas.number, corps_guid=corps_guid)
            db.add(room)
            await db.commit()
            await db.refresh(room)
        return room

    # Teacher create
    @staticmethod
    @celery.task
    async def teacher_create(schemas: TeacherCreateSchema) -> TeacherModel:
        async with get_session() as db:
            teacher = await TeacherRepository.get_by_name(db, schemas.name, schemas.lang)

            if teacher is not None:
                raise HTTPException(409, "Преподаватель уже существует")

            teacher = TeacherModel(online_url=schemas.online_url, alt_online_url=schemas.alt_online_url)
            db.add(teacher)
            await db.commit()
            await db.refresh(teacher)
        return teacher

    # Lesson create
    @staticmethod
    @celery.task
    async def lesson_create(schemas: LessonCreateSchema) -> LessonModel:
        async with get_session() as db:
            lesson = await LessonRepository.get_unique(db, schemas)

            if lesson is not None:
                raise HTTPException(409, detail="Занятие уже существует")

            lesson = LessonModel(time_start=schemas.time_start,
                                 time_end=schemas.time_end,
                                 dot=schemas.dot,
                                 weeks=schemas.weeks,
                                 day=schemas.day,
                                 date_start=schemas.date_start,
                                 date_end=schemas.date_end)

            lesson = await LessonRepository.set_dependencies(db,
                                                             lesson,
                                                             group=schemas.group,
                                                             room=schemas.room,
                                                             teacher_name=schemas.teacher_name,
                                                             lang=schemas.lang)

            db.add(lesson)
            await db.commit()
            await db.refresh(lesson)

        return lesson.guid

    @staticmethod
    @celery.task
    async def set_dependencies(db: AsyncSession,
                               lesson: LessonModel,
                               group: str,
                               room: str,
                               teacher_name: str,
                               lang: str) -> LessonModel:
        group = await GroupRepository.get_by_name(db, group)
        if group is not None:
            lesson.groups.append(group)

        room = await RoomRepository.get_by_number(db, room)
        if room is not None:
            lesson.rooms.append(room)

        teacher = await TeacherRepository.get_by_name(db, teacher_name, lang)
        if teacher is not None:
            lesson.teachers.append(teacher)

        return lesson

    @staticmethod
    @celery.task
    async def teacher_update(schemas: TeacherCreateSchema) -> None:
        async with get_session() as db:
            teacher = await TeacherRepository.get_by_name(db, name=schemas.name, lang=schemas.lang)

            if teacher is None:
                raise HTTPException(404, "Преподавателя не существует")

            await db.execute(update(TeacherTranslateModel)
                             .where(TeacherTranslateModel.teacher_guid == teacher.guid)
                             .values(name=schemas.name,
                                     fullname=schemas.fullname,
                                     lang=schemas.lang,
                                     teacher_guid=teacher.guid))
            await db.execute(update(TeacherModel).where(TeacherModel.guid == teacher.guid)
                             .values(online_url=schemas.online_url,
                                     alt_online_url=schemas.alt_online_url))

            await db.commit()
            await db.refresh(teacher)

        return teacher
