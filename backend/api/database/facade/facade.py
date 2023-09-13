import datetime
from abc import ABC
from typing import List, Optional, Tuple

from fastapi import HTTPException
from pydantic import UUID4, BaseModel
from sqlalchemy import and_, between, delete, desc, insert, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.database.facade.interface import IFacadeDB
from backend.api.database.models import (
    AcademicModel,
    CorpsModel,
    GroupModel,
    LessonModel,
    LessonTranslateModel,
    NewsModel,
    RoomModel,
    StartSemesterModel,
)
from backend.api.database.models.association_tables import AT_lesson_group, AT_lesson_room, AT_lesson_teacher
from backend.api.database.models.news_image import NewsImageModel
from backend.api.database.models.teacher import TeacherModel
from backend.api.filters.room import RoomFilter
from backend.api.schemas.academic import AcademicCreateSchema
from backend.api.schemas.corps import CorpsCreateSchema
from backend.api.schemas.group import GroupCreateSchema
from backend.api.schemas.lesson import LessonCreateSchema
from backend.api.schemas.lesson_translate import LessonTranslateCreateSchema
from backend.api.schemas.news import NewsCreateSchema
from backend.api.schemas.room import RoomCreateSchema
from backend.api.schemas.start_semester import StartSemesterCreateSchema
from backend.api.schemas.teacher import TeacherCreateSchema
from etl.schemas.lesson import LessonLoading


class FacadeDB(IFacadeDB, ABC):
    session: AsyncSession

    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_alive(self) -> bool:
        try:
            await self.session.execute("SELECT 1")
        except Exception:
            return False
        return True

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, model: BaseModel) -> BaseModel:
        await self.session.refresh(model)
        return model

    async def rollback(self) -> None:
        await self.session.rollback()

    async def create_academic(self, data: AcademicCreateSchema) -> AcademicModel:
        academic = AcademicModel(**data.model_dump())
        self.session.add(academic)
        await self.session.flush()
        await self.session.refresh(academic)
        return academic

    async def bulk_insert_academic(self, data: List[AcademicCreateSchema]) -> None:
        insert_data = [AcademicModel(**academic.model_dump()) for academic in data]
        self.session.add_all(insert_data)
        await self.session.flush()

    async def get_by_id_academic(self, guid: UUID4) -> AcademicModel:
        academic = await self.session.execute(select(AcademicModel). where(AcademicModel.guid == guid).limit(1))
        return academic.scalar()

    async def get_by_name_academic(self, name: str) -> AcademicModel:
        academic = await self.session.execute(select(AcademicModel).where(AcademicModel.name == name).limit(1))
        return academic.scalar()

    async def update_academic(self, guid: UUID4, data: AcademicCreateSchema) -> AcademicModel:
        academic = await self.get_by_id_academic(guid)

        if academic is None:
            HTTPException(status_code=404, detail="Ученое звание не найден")

        await self.session.execute(update(AcademicModel).where(AcademicModel.guid == guid).values(**data.model_dump()))
        await self.session.flush()
        await self.session.refresh(academic)

        return academic

    async def delete_academic(self, guid: UUID4) -> None:
        await self.session.execute(delete(AcademicModel).where(AcademicModel.guid == guid))
        await self.session.flush()

    async def create_corps(self, data: CorpsCreateSchema) -> CorpsModel:
        corps = CorpsModel(**data.model_dump())
        self.session.add(corps)
        await self.session.flush()
        await self.session.refresh(corps)
        return corps

    async def bulk_insert_corps(self, data: List[CorpsCreateSchema]) -> None:
        insert_data = [CorpsModel(**corps.model_dump()) for corps in data]
        self.session.add_all(insert_data)
        await self.session.flush()

    async def get_by_id_corps(self, guid: UUID4) -> CorpsModel:
        corps = await self.session.execute(select(CorpsModel).where(CorpsModel.guid == guid).limit(1))
        return corps.scalar()

    async def get_by_name_corps(self, name: str) -> CorpsModel:
        corps = await self.session.execute(select(CorpsModel).where(CorpsModel.name == name).limit(1))
        return corps.scalar()

    async def get_all_corps(self) -> List[CorpsModel]:
        corps = await self.session.execute(select(CorpsModel.name).distinct())
        return corps.scalars().all()

    async def update_corps(self, guid: UUID4, data: CorpsCreateSchema) -> CorpsModel:
        corps = await self.get_by_id_corps(guid)

        if corps is None:
            HTTPException(status_code=404, detail="Корпус не найден")

        await self.session.execute(update(CorpsModel).where(CorpsModel.guid == guid).values(**data.model_dump()))
        await self.session.flush()
        await self.session.refresh(corps)

        return corps

    async def delete_corps(self, guid: UUID4) -> None:
        await self.session.execute(delete(CorpsModel).where(CorpsModel.guid == guid))
        await self.session.flush()

    async def create_group(self, data: GroupCreateSchema, academic_guid: UUID4) -> GroupModel:
        group = GroupModel(name=data.name, course=data.course, academic_guid=academic_guid)
        self.session.add(group)
        await self.session.flush()
        await self.session.refresh(group)
        return group

    async def bulk_insert_group(self, data: List[GroupCreateSchema]) -> None:
        insert_data = [GroupModel(**group.model_dump()) for group in data]
        self.session.add_all(insert_data)
        await self.session.flush()

    async def get_by_id_group(self, guid: UUID4) -> GroupModel:
        group = await self.session.execute(select(GroupModel).where(GroupModel.guid == guid).limit(1))
        return group.scalar()

    async def get_all_group(self) -> List[str]:
        groups = await self.session.execute(select(GroupModel.name))
        return groups.scalars().unique().all()

    async def get_by_name_group(self, name: str) -> GroupModel:
        group = await self.session.execute(select(GroupModel).where(GroupModel.name == name).limit(1))
        return group.scalar()

    async def update_group(self, guid: UUID4, data: GroupCreateSchema) -> GroupModel:
        group = await self.session.get_by_id_group(self.session, guid)

        if group is None:
            HTTPException(status_code=404, detail="Группа не найдена")

        group = await self.session.execute(update(GroupModel).where(GroupModel.guid == guid).values(**data.model_dump()))
        await self.session.flush()
        await self.session.refresh(group)
        return group

    async def delete_group(self, guid: UUID4) -> None:
        await self.session.execute(delete(GroupModel).where(GroupModel.guid == guid))
        await self.session.flush()

    async def create_lesson(self, data: LessonCreateSchema) -> LessonModel:
        lesson = LessonModel(
            time_start=data.time_start,
            time_end=data.time_end,
            dot=data.dot,
            weeks=data.weeks,
            day=data.day,
            date_start=data.date_start,
            date_end=data.date_end
        )

        lesson = await self.set_dependencies(
            lesson=lesson,
            groups=[data.group],
            rooms=[data.room],
            teachers=[data.teacher_name]
        )

        self.session.add(lesson)
        await self.session.flush()
        await self.session.refresh(lesson)

        return lesson

    async def set_dependencies(
            self,
            lesson: LessonModel,
            groups: List[str],
            rooms: List[str],
            teachers: List[str],
    ) -> LessonModel:
        
        for group in groups:
            g = await self.get_by_name_group(group)
            if g is not None:
                lesson.groups.add(g)

        for room in rooms:
            r = await self.get_by_number_room(room)
            if r is not None:
                lesson.rooms.add(r)

        for teacher in teachers:
            t = await self.get_by_name_teacher(teacher)
            if t is not None:
                lesson.teachers.add(t)

        return lesson

    async def bulk_insert_lesson(self, data: List[LessonLoading]) -> None:
        db_lessons = []

        for lesson in data:
            db_lesson = LessonModel(
                time_start=lesson.time_start,
                time_end=lesson.time_end,
                dot=lesson.dot,
                weeks=lesson.weeks,
                day=lesson.day,
                date_start=lesson.date_start,
                date_end=lesson.date_end
            )

            # insert(LessonModel).values(**db_lesson.model_dump())

            self.session.add(db_lesson)

            db_lesson = await self.set_dependencies(
                lesson=db_lesson,
                groups=lesson.groups,
                rooms=lesson.rooms,
                teachers=lesson.teachers
            )

            db_lessons.append(db_lesson)

        # self.session.add_all(db_lessons)
        await self.session.flush()

    async def get_by_id_lesson(self, guid: UUID4) -> LessonModel:
        lesson = await self.session.execute(select(LessonModel).where(LessonModel.guid == guid).limit(1))
        return lesson.scalar()

    async def get_unique_lesson(self, data: LessonCreateSchema) -> LessonModel:
        lesson_translate_subq = (
            select(LessonTranslateModel.lesson_guid)
            .where(
                (LessonTranslateModel.name == data.name) &
                (LessonTranslateModel.subgroup == data.subgroup) &
                (LessonTranslateModel.type == data.type) &
                (LessonTranslateModel.lang == data.lang)
            )
            .limit(1)
            .subquery()
        )

        teacher_subq = (
            select(TeacherModel.guid)
            .where(
                (TeacherModel.name == data.teacher_name) &
                (TeacherModel.lang == data.lang)
            )
            .limit(1)
            .subquery()
        )

        group_subq = (
            select(GroupModel.guid)
            .where(GroupModel.name == data.group)
            .limit(1)
            .subquery()
        )

        room_subq = (
            select(RoomModel.guid)
            .where(RoomModel.number == data.room)
            .limit(1)
            .subquery()
        )

        lesson_query = (
            select(LessonModel)
            .join(AT_lesson_room, LessonModel.guid == AT_lesson_room.c.lesson_guid)
            .join(AT_lesson_group, LessonModel.guid == AT_lesson_group.c.lesson_guid)
            .join(AT_lesson_teacher, LessonModel.guid == AT_lesson_teacher.c.lesson_guid)
            .join(lesson_translate_subq, LessonModel.guid == lesson_translate_subq.c.lesson_guid)
            .where(
                (LessonModel.time_start == data.time_start) &
                (LessonModel.time_end == data.time_end) &
                (LessonModel.dot == data.dot) &
                (LessonModel.weeks == data.weeks) &
                (LessonModel.date_start == data.date_start) &
                (LessonModel.date_end == data.date_end) &
                (LessonModel.day == data.day) &
                (AT_lesson_room.c.room_guid == room_subq) &
                (AT_lesson_group.c.group_guid == group_subq) &
                (AT_lesson_teacher.c.teacher_guid == teacher_subq)
            )
            .limit(1)
        )

        lesson = await self.session.execute(lesson_query)
        return lesson.scalar()

    async def get_lesson_lesson(self, data: LessonCreateSchema) -> LessonModel:
        lesson_translate_subq = (
            select(LessonTranslateModel.lesson_guid)
            .where(
                (LessonTranslateModel.name == data.name) &
                (LessonTranslateModel.subgroup == data.subgroup) &
                (LessonTranslateModel.type == data.type) &
                (LessonTranslateModel.lang == data.lang)
            )
            .limit(1)
            .scalar_subquery()
        )

        room_subq = (
            select(RoomModel.guid)
            .where(RoomModel.number == data.room)
            .limit(1)
            .scalar_subquery()
        )

        lesson_room_subq = (
            select(AT_lesson_room.c.lesson_guid)
            .where(AT_lesson_room.c.room_guid == room_subq)
            .limit(1)
            .scalar_subquery()
        )

        lesson_query = (
            select(LessonModel)
            .join(
                lesson_translate_subq,
                LessonModel.guid == lesson_translate_subq
            )
            .join(
                lesson_room_subq,
                LessonModel.guid == lesson_room_subq
            )
            .where(
                (LessonModel.time_start == data.time_start) &
                (LessonModel.time_end == data.time_end) &
                (LessonModel.dot == data.dot) &
                (LessonModel.weeks == data.weeks) &
                (LessonModel.date_start == data.date_start) &
                (LessonModel.date_end == data.date_end) &
                (LessonModel.day == data.day)
            )
            .limit(1)
        )

        return await self.session.scalar(lesson_query)

    async def get_id_lesson(self, data: LessonCreateSchema) -> UUID4:
        lesson_translate_subq = (
            select(LessonTranslateModel.lesson_guid)
            .where(
                (LessonTranslateModel.name == data.name) &
                (LessonTranslateModel.subgroup == data.subgroup) &
                (LessonTranslateModel.type == data.type) &
                (LessonTranslateModel.lang == data.lang)
            )
            .limit(1)
            .subquery()
        )

        room_subq = (
            select(RoomModel.guid)
            .where(RoomModel.number == data.room)
            .limit(1)
            .scalar_subquery()
        )

        lesson_room_subq = (
            select(AT_lesson_room.c.lesson_guid)
            .where(AT_lesson_room.c.room_guid == room_subq)
            .subquery()
        )

        lesson_query = (
            select(LessonModel.guid)
            .join(lesson_translate_subq, LessonModel.guid == lesson_translate_subq.c.lesson_guid)
            .join(lesson_room_subq, LessonModel.guid == lesson_room_subq.c.lesson_guid)
            .where(
                (LessonModel.time_start == data.time_start) &
                (LessonModel.time_end == data.time_end) &
                (LessonModel.dot == data.dot) &
                (LessonModel.weeks == data.weeks) &
                (LessonModel.date_start == data.date_start) &
                (LessonModel.date_end == data.date_end) &
                (LessonModel.day == data.day)
            )
            .limit(1)
        )

        lesson = await self.session.execute(lesson_query)
        return lesson.scalar()

    async def get_by_group_lesson(self, group: str, lang: str, date_: datetime.date = datetime.date.today()) -> \
            List[LessonModel]:
        lessons = await self.session.execute(
            select(LessonModel)
            .join(
                LessonTranslateModel,
                LessonTranslateModel.lesson_guid == LessonModel.guid
            )
            .join(
                AT_lesson_group,
                AT_lesson_group.c.lesson_guid == LessonModel.guid
            )
            .join(
                GroupModel,
                GroupModel.guid == AT_lesson_group.c.group_guid
            )
            .where(
                GroupModel.name == group and
                LessonTranslateModel.lang == lang and
                (LessonModel.date_start <= date_ <= LessonModel.date_end)
            )
        )
        return lessons.scalars().unique().all()

    async def get_by_teacher_lesson(self, teacher: str, lang: str, date_: datetime.date = datetime.date.today()) -> \
            List[LessonModel]:
        lessons = await self.session.execute(
            select(LessonModel)
            .join(
                AT_lesson_teacher,
                AT_lesson_teacher.c.lesson_guid == LessonModel.guid
            )
            .where(
                TeacherModel.name == teacher and
                TeacherModel.lang == lang and
                and_(
                    LessonModel.date_start is not None,
                    and_(
                        LessonModel.date_end is not None,
                        between(date_, LessonModel.date_start, LessonModel.date_end)
                    )
                )
            )
        )
        return lessons.scalars().unique().all()

    async def update_lesson(self, guid: UUID4, data: LessonCreateSchema) -> LessonModel:
        lesson = await self.get_by_id_lesson(guid)
        lesson_translate = await self.get_by_name_lesson_translate(data.name, data.lang)

        if lesson is None:
            HTTPException(status_code=404, detail="Занятие не найдено")

        if lesson_translate is None:
            HTTPException(status_code=404, detail="Перевода занятия не существует")

        await self.session.execute(
            update(LessonModel)
            .where(LessonModel.guid == guid)
            .values(
                time_start=data.time_start,
                time_end=data.time_end,
                dot=data.dot,
                weeks=data.weeks,
                date_start=data.date_start,
                date_end=data.date_end,
                day=data.day
            )
        )
        await self.session.execute(
            update(LessonModel)
            .where(LessonTranslateModel.guid == lesson_translate.guid)
            .values(
                type=data.type,
                name=data.name,
                subgroup=data.subgroup,
                lang=data.lang
            )
        )
        await self.session.flush()
        await self.session.refresh(lesson)

        return lesson

    async def update_translate_lesson(self, data: LessonCreateSchema, guid: str) -> LessonModel:
        lesson = await self.get_by_id_lesson(guid)

        if lesson is None:
            HTTPException(status_code=404, detail="Занятие не найдено")

        for trans in lesson.trans:
            if trans.lang == data.lang:
                HTTPException(status_code=404, detail="Занятие на этом языке существует")

        trans = LessonTranslateModel(
            type=data.type,
            name=data.name,
            subgroup=data.subgroup,
            lang=data.lang,
            lesson_guid=lesson.guid
        )
        lesson.trans.append(trans)

        await self.session.flush()
        await self.session.refresh(lesson)

        return lesson

    async def delete_lesson(self, guid: UUID4) -> None:
        await self.session.execute(delete(LessonModel).where(LessonModel.guid == guid))
        await self.session.flush()

    async def create_lesson_translate(self, data: LessonTranslateCreateSchema) -> LessonTranslateModel:
        lesson_tr = LessonTranslateModel(**data.model_dump())
        self.session.add(lesson_tr)

        await self.session.flush()
        await self.session.refresh(lesson_tr)

        return lesson_tr

    async def get_by_id_lesson_translate(self, guid: UUID4) -> LessonTranslateModel:
        lesson_tr = await self.session.execute(
            select(LessonTranslateModel)
            .where(LessonTranslateModel.guid == guid)
            .limit(1))
        return lesson_tr.scalar()

    async def get_unique_lesson_translate(
            self,
            type_: str,
            name: str,
            subgroup: Optional[str],
            lang: str
    ) -> LessonTranslateModel:
        lesson_tr = await self.session.execute(
            select(LessonTranslateModel)
            .where(
                LessonTranslateModel.type == type_ and
                LessonTranslateModel.name == name and
                LessonTranslateModel.subgroup == subgroup and
                LessonTranslateModel.lang == lang
            )
            .limit(1)
        )
        return lesson_tr.scalar()

    async def get_by_name_lesson_translate(self, name: str, lang: str) -> LessonTranslateModel:
        lesson_tr = await self.session.execute(
            select(LessonTranslateModel)
            .where(
                LessonTranslateModel.name == name and
                LessonTranslateModel.lang == lang
            )
            .limit(1)
        )
        return lesson_tr.scalar()

    async def get_by_lesson_guid_lesson_translate(self, guid: UUID4, lang: str) -> LessonTranslateModel:
        lesson_tr = await self.session.execute(
            select(LessonTranslateModel)
            .where(
                LessonTranslateModel.lesson_guid == guid and
                LessonTranslateModel.lang == lang
            ).
            limit(1)
        )
        return lesson_tr.scalar()

    async def update_lesson_translate(self, guid: UUID4, data: LessonTranslateCreateSchema) -> LessonTranslateModel:
        lesson_tr = await self.get_by_id_lesson_translate(guid)

        if lesson_tr is None:
            HTTPException(status_code=404, detail="Перевод (занятие) не найден")

        lesson_tr = await self.session.execute(
            update(LessonTranslateModel)
            .where(LessonTranslateModel.guid == guid)
            .values(**data.model_dump()))

        await self.session.flush()
        await self.session.refresh(lesson_tr)

        return lesson_tr

    async def delete_lesson_translate(self, guid: UUID4) -> None:
        await self.session.execute(delete(LessonTranslateModel).where(LessonTranslateModel.guid == guid))
        await self.session.flush()

    async def get_by_id_news(self, guid: UUID4) -> NewsModel:
        news = await self.session.execute(select(NewsModel).where(NewsModel.guid == guid).limit(1))
        return news.scalar()

    async def get_by_news_id_news(self, news_id: str) -> NewsModel:
        news = await self.session.execute(select(NewsModel).where(NewsModel.news_id == news_id).limit(1))
        return news.scalar()

    async def get_all_news(self, tag: str, offset: int, limit: int = 100) -> List[NewsModel]:
        news = await self.session.execute(
            select(NewsModel)
            .where(NewsModel.tag == tag)
            .order_by(desc(NewsModel.date))
            .offset(offset)
            .limit(limit)
        )
        return news.scalars().unique().all()

    async def bulk_insert_news(self, data: List[NewsCreateSchema]) -> None:
        insert_data = []
        for news in data:
            imgs = [
                NewsImageModel(url=img.url, text=img.text) 
                for img in news.imgs
            ]
            insert_data.append(
                NewsModel(
                    news_id=news.news_id,
                    title=news.title,
                    preview_url=news.preview_url,
                    date=news.date,
                    text=news.text,
                    tag=news.tag,
                    imgs=imgs
                )
            )
        self.session.add_all(insert_data)
        await self.session.flush()

    async def delete_news(self, guid: UUID4) -> None:
        await self.session.execute(delete(NewsModel).where(NewsModel.guid == guid))
        await self.session.flush()

    async def create_room(self, data: RoomCreateSchema, corps_guid) -> RoomModel:
        room = RoomModel(number=data.number, corps_guid=corps_guid)

        self.session.add(room)
        await self.session.flush()
        await self.session.refresh(room)

        return room

    async def bulk_insert_room(self, data: List[RoomCreateSchema]) -> None:
        db_rooms = []

        for room in data:
            corps = await self.get_by_name_corps(room.corps)
            db_rooms.append(RoomModel(number=room.number, corps_guid=corps.guid if corps else None))

        self.session.add_all(db_rooms)
        await self.session.flush()

    async def get_by_id_room(self, guid: UUID4) -> RoomModel:
        room = await self.session.execute(select(RoomModel).where(RoomModel.guid == guid).limit(1))
        return room.scalar()

    async def get_all_room(self) -> List[RoomModel]:
        rooms = await self.session.execute(select(RoomModel))
        return rooms.scalars().unique().all()

    async def get_by_number_room(self, number: str) -> RoomModel:
        room = await self.session.execute(select(RoomModel).where(RoomModel.number == number).limit(1))
        return room.scalar()

    async def get_empty_room(self, room_filter: RoomFilter, corps: List[str])\
            -> List[Tuple[str, datetime.time, datetime.time, str]]:
        date = await self.get_start_semester()

        if date is None:
            raise HTTPException(409, "Даты начала семестра нет")

        week = (room_filter.date_ - date.date).days // 7 + 1
        if week == 2:
            week = [0, 1, 2]
        elif week == 1:
            week = [1, 2]
        else:
            week = [0, 2]

        occupied_rooms = await self.session.execute(
            select(
                RoomModel.number.label("room_number"),
                LessonModel.time_start.label("lesson_time_start"),
                LessonModel.time_end.label("lesson_time_end"),
                CorpsModel.name.label("corps_name")
            )
            .join(RoomModel.lessons)
            .join(RoomModel.corps)
            .where(
                and_(
                    CorpsModel.name.in_(corps),
                    LessonModel.day == weekdays[room_filter.date_.weekday()],
                    LessonModel.weeks.in_(week),
                    or_(

                        LessonModel.date_start.is_(None),
                        and_(
                            LessonModel.date_start == room_filter.date_,
                            LessonModel.date_end.is_(None)
                        ),
                        and_(
                            LessonModel.date_start <= room_filter.date_,
                            LessonModel.date_end >= room_filter.date_
                        )
                    ),
                    or_(
                        and_(
                            LessonModel.time_start >= room_filter.time_start,
                            LessonModel.time_start <= room_filter.time_end
                        ),
                        and_(
                            LessonModel.time_end >= room_filter.time_start,
                            LessonModel.time_end <= room_filter.time_end
                        ),
                        and_(
                            LessonModel.time_start < room_filter.time_start,
                            LessonModel.time_end > room_filter.time_end
                        )
                    )
                )
            )
            .distinct().order_by(RoomModel.number, LessonModel.time_start)
        )

        occupied_rooms = occupied_rooms.all()

        occupied_rooms_numbers = (room[0] for room in occupied_rooms)
        full_time_free_rooms = await self.session.execute(
            select(
                RoomModel.number.label("room_number"),
                CorpsModel.name.label("corps_name")
            )
            .join(RoomModel.corps)
            .where(
                and_(
                    CorpsModel.name.in_(corps),
                    RoomModel.number.notin_(occupied_rooms_numbers)
                )
            )
        )

        full_time_free_rooms = full_time_free_rooms.all()

        last_room = None
        free_rooms = []
        deltatime = datetime.timedelta(minutes=10)
        for room in occupied_rooms:
            if last_room is None:
                if room[1] > room_filter.time_start and \
                        self.sub_time(room[1], room_filter.time_start) > deltatime:
                    free_rooms.append((room[0], room_filter.time_start, room[1], room[3]))
                last_room = room
                continue

            if last_room[0] == room[0]:
                if self.sub_time(last_room[2], room[1]) > deltatime:
                    free_rooms.append((last_room[0], last_room[2], room[1], last_room[3]))
                last_room = room
                continue

            if last_room[2] < room_filter.time_end and \
                    self.sub_time(last_room[2], room_filter.time_end) > deltatime:
                free_rooms.append((last_room[0], last_room[2], room_filter.time_end, last_room[3]))

            if room[1] > room_filter.time_start and \
                    self.sub_time(room[1], room_filter.time_start) > deltatime:
                free_rooms.append((room[0], room_filter.time_start, room[1], room[3]))
            last_room = room

        free_rooms.extend(
            (room[0], room_filter.time_start, room_filter.time_end, room[1])
            for room in full_time_free_rooms
        )
        return free_rooms

    @staticmethod
    def sub_time(time1: datetime.time, time2: datetime.time) -> datetime.timedelta:
        datetime1 = datetime.datetime.combine(datetime.date.today(), time1)
        datetime2 = datetime.datetime.combine(datetime.date.today(), time2)
        return datetime2 - datetime1

    async def update_room(self, guid: UUID4, data: RoomCreateSchema) -> RoomModel:
        room = await self.get_by_id_room(guid)

        if room is None:
            HTTPException(status_code=404, detail="Кабинет не найден")

        room = await self.session.execute(update(RoomModel).where(RoomModel.guid == guid).values(**data.model_dump()))
        await self.session.flush()
        await self.session.refresh(room)
        return room

    async def delete_room(self, guid: UUID4) -> None:
        await self.session.execute(delete(RoomModel).where(RoomModel.guid == guid))
        await self.session.flush()

    async def create_start_semester(self, data: StartSemesterCreateSchema) -> StartSemesterModel:
        start_semester = StartSemesterModel(**data.model_dump())

        self.session.add(start_semester)
        await self.session.flush()
        await self.session.refresh(start_semester)

        return start_semester

    async def get_start_semester(self) -> StartSemesterModel:
        start_semester = await self.session.execute(select(StartSemesterModel).limit(1))
        return start_semester.scalar()

    async def update_start_semester(self, data: StartSemesterCreateSchema) -> StartSemesterModel:
        start_semester = await self.get_start_semester()

        if start_semester is None:
            raise HTTPException(404, "Даты не существует")

        await self.session.execute(
            update(StartSemesterModel)
            .where(StartSemesterModel.guid == start_semester.guid)
            .values(**data.model_dump())
        )
        await self.session.flush()
        await self.session.refresh(start_semester)
        return start_semester

    async def create_teacher(self, data: TeacherCreateSchema) -> TeacherModel:
        teacher = TeacherModel(**data.model_dump())

        self.session.add(teacher)
        await self.session.flush()
        await self.session.refresh(teacher)

        return teacher

    async def bulk_insert_teacher(self, data: List[TeacherCreateSchema]) -> None:
        db_teachers = [TeacherModel(**teacher.model_dump()) for teacher in data]
        self.session.add_all(db_teachers)
        await self.session.flush()

    async def get_by_id_teacher(self, guid: UUID4) -> TeacherModel:
        teacher = await self.session.execute(select(TeacherModel).where(TeacherModel.guid == guid).limit(1))
        return teacher.scalar()

    async def get_all_teacher(self, lang: str) -> List[str]:
        teachers = await self.session.execute(select(TeacherModel.name).where(TeacherModel.lang == lang))
        return teachers.scalars().unique().all()

    async def get_by_name_teacher(self, name: str) -> TeacherModel:
        teacher = await self.session.execute(select(TeacherModel).where(TeacherModel.name == name).limit(1))
        return teacher.scalar()

    async def get_unique_teacher(self, data: TeacherCreateSchema) -> TeacherModel:
        teacher = await self.session.execute(
            select(TeacherModel)
            .where(
                TeacherModel.name == data.name and
                TeacherModel.lang == data.lang and
                TeacherModel.fullname == data.fullname
            )
            .limit(1)
        )
        return teacher.scalar()

    async def update_teacher(self, guid: UUID4, data: TeacherCreateSchema) -> TeacherModel:
        teacher = await self.get_by_name_teacher(data.name)

        if teacher is None:
            raise HTTPException(404, "Преподавателя не существует")

        await self.session.execute(update(TeacherModel).where(TeacherModel.guid == guid).values(**data.model_dump()))

        await self.session.flush()
        await self.session.refresh(teacher)

        return teacher

    async def delete_teacher(self, guid: UUID4) -> None:
        await self.session.execute(delete(TeacherModel).where(TeacherModel.guid == guid))
        await self.session.flush()
