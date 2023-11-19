from sqlalchemy.ext.asyncio import AsyncSession

from utils.version import Version


async def get_academic_service(version: Version, session: AsyncSession):
    if version >= "0.0.1":
        from .v0_0_1 import AcademicService

        return AcademicService(version=version, session=session)


async def get_corps_service(version: Version, session: AsyncSession):
    if version >= "0.0.1":
        from .v0_0_1 import CorpsService

        return CorpsService(version=version, session=session)


async def get_group_service(version: Version, session: AsyncSession):
    if version >= "0.0.1":
        from .v0_0_1 import GroupService

        return GroupService(version=version, session=session)


async def get_lesson_service(version: Version, session: AsyncSession):
    if version >= "0.0.1":
        from .v0_0_1 import LessonService

        return LessonService(version=version, session=session)


async def get_news_service(version: Version, session: AsyncSession):
    if version >= "0.0.1":
        from .v0_0_1 import NewsService

        return NewsService(version=version, session=session)


async def get_room_service(version: Version, session: AsyncSession):
    if version >= "0.0.1":
        from .v0_0_1 import RoomService

        return RoomService(version=version, session=session)


async def get_start_semester_service(version: Version, session: AsyncSession):
    if version >= "0.0.1":
        from .v0_0_1 import StartSemesterService

        return StartSemesterService(version=version, session=session)


async def get_teacher_service(version: Version, session: AsyncSession):
    if version >= "0.0.1":
        from .v0_0_1 import TeacherService

        return TeacherService(version=version, session=session)
