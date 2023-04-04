import datetime
import json
import traceback
from copy import deepcopy
from os import getcwd

import sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from translate_schedule import translate_lessons
from translate_teachers import translate_teachers
from WrapLessonModel import WrapLessonModel

from backend.database.models.academic import AcademicModel
from backend.database.models.corps import CorpsModel
from backend.database.models.group import GroupModel
from backend.database.models.lesson import LessonModel
from backend.database.models.lesson_translate import LessonTranslateModel
from backend.database.models.room import RoomModel
from backend.database.models.teacher import TeacherModel
from backend.database.models.teacher_translate import TeacherTranslateModel
from parsing.parsers.schedule_parser import ScheduleParser


async def bulk_insert_academic(db: AsyncSession) -> None:
    try:
        async with db.begin():
            parser = ScheduleParser()
            res = set(AcademicModel(name=academic[0]) for academic in parser.getAcademicTypes())
            print(f'Inserting {len(res)} items')
            db.add_all(res)
            await db.commit()
            print('Committed changes')
    except sqlalchemy.exc.IntegrityError as e:
        print(f'Error: {str(e)}')
        await db.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        await db.rollback()


async def bulk_insert_groups(db: AsyncSession) -> None:
    __academic__ = None
    try:
        async with db.begin():
            print(f'Groups inserting')
            academics_sc = await db.execute(select(AcademicModel.name, AcademicModel.guid))
            rows = academics_sc.fetchall()
            academics = {}
            for row in rows:
                academics[row[0]] = row[1]

            res = []
            parser = ScheduleParser()
            for academic in parser.getAcademicTypes():
                __academic__ = academic[0]
                with open(f'{getcwd()}/parsing/schedule/{academic[0]}.json', 'r', encoding='utf-8') as fp:
                    dict_json = json.loads(fp.read().replace("'", '\''))
                    for course in dict_json['courses']:
                        for group in course['groups']:
                            res.append(GroupModel(
                                name=group['name'],
                                course=course['name'],
                                academic_guid=academics[dict_json['name']]
                            ))
            print(f'Inserting {len(res)} items')
            db.add_all(res)
            await db.commit()
            print('Committed changes')
    except FileNotFoundError:
        print(f'File {__academic__}.json was not found.')
    except sqlalchemy.exc.IntegrityError as e:
        print(f'Error: {str(e)}')
        await db.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        await db.rollback()


async def bulk_insert_schedule(db: AsyncSession) -> None:
    __academic__ = None
    try:
        async with db.begin():
            print(f'Schedule inserting')
            i = 0
            res_lessons = set()
            parser = ScheduleParser()
            for academic in parser.getAcademicTypes():
                __academic__ = academic[0]
                with open(f'{getcwd()}/parsing/schedule/{academic[0]}.json', 'r', encoding='utf-8') as fp:
                    dict_json = json.loads(fp.read().replace("'", '\''))
                    for course in dict_json['courses']:
                        for group in course['groups']:
                            for day in group['schedule']:
                                for lesson in day['lessons']:
                                    for lesson_var in lesson['lesson']:
                                        teacher_schema = set()
                                        for teacher in lesson_var['teacher_name']:
                                            teacher_schema.add(teacher)
                                        room_schema = lesson_var['room']
                                        group_schema = {group['name']}

                                        time_start = datetime.datetime.strptime(lesson['time_start'], "%H:%M").time()
                                        time_end = datetime.datetime.strptime(lesson['time_end'], "%H:%M").time()

                                        date_start = lesson_var['date_start'].split('.') \
                                            if lesson_var['date_start'] is not None else None

                                        if date_start is not None:
                                            date_start.reverse()
                                            date_start = datetime.datetime.strptime("-".join(date_start),
                                                                                    '%Y-%m-%d').date()

                                        date_end = lesson_var['date_end'].split('.') \
                                            if lesson_var['date_end'] is not None else None

                                        if date_end is not None:
                                            date_end.reverse()
                                            date_end = datetime.datetime.strptime("-".join(date_end), '%Y-%m-%d').date()

                                        lesson_schema = WrapLessonModel(LessonModel(
                                            time_start=time_start,
                                            time_end=time_end,
                                            dot=lesson_var['dot'],
                                            weeks=lesson_var['weeks'],
                                            day=day['day'],
                                            date_start=date_start,
                                            date_end=date_end,
                                            teachers=[],
                                            groups=[],
                                            rooms=[],
                                            trans=[LessonTranslateModel(
                                                name=lesson_var['lesson_name'],
                                                subgroup=lesson_var['subgroup'],
                                                lang='ru',
                                                type=lesson_var['lesson_type']
                                            )]
                                        ), teachers=deepcopy(teacher_schema),
                                            groups=deepcopy(group_schema),
                                            rooms=room_schema)

                                        i += 1

                                        if lesson_schema in res_lessons:
                                            for l in res_lessons:
                                                if l == lesson_schema:
                                                    lesson_schema.teachers.update(l.teachers)
                                                    lesson_schema.groups.update(l.groups)
                                                    res_lessons.remove(l)
                                                    break
                                        res_lessons.add(lesson_schema)

            groups_sc = await db.execute(select(GroupModel))
            groups_sc = groups_sc.unique().scalars().all()
            groups = {}
            for group in groups_sc:
                groups[group.name] = group

            corps_sc = await db.execute(select(CorpsModel))
            corps_sc = corps_sc.unique().scalars().all()
            corps = {}
            for c in corps_sc:
                corps[c.name] = c

            room_sc = await db.execute(select(RoomModel))
            room_sc = room_sc.unique().scalars().all()
            rooms = {}
            all_rooms = []
            for room in room_sc:
                all_rooms.append(room.number)
                rooms[room.number] = room

            teacher_sc = await db.execute(select(TeacherModel))
            teacher_sc = teacher_sc.unique().scalars().all()
            teachers = {}
            all_teachers = []
            for teacher in teacher_sc:
                all_teachers.append(teacher.trans[0].name)
                teachers[teacher.trans[0].name] = teacher

            res = []
            for item in res_lessons:
                new_teachers = []
                for teacher in item.teachers:
                    if teacher in all_teachers:
                        new_teachers.append(teachers[teacher])
                    elif teacher is not None:
                        _ = TeacherModel(
                            online_url=None,
                            alt_online_url=None,
                            trans=[TeacherTranslateModel(
                                name=teacher,
                                fullname=None,
                                lang='ru'
                            )]
                        )
                        db.add(_)
                        new_teachers.append(_)
                item.teachers = new_teachers

                new_rooms = []
                r = item.rooms
                if r in all_rooms:
                    new_rooms.append(rooms[r])
                elif r is not None:
                    _ = RoomModel(
                        number=r,
                        corps=corps["Корпус Нет корпуса"]
                    )
                    db.add(_)
                    new_rooms.append(_)

                new_groups = []
                for g in item.groups:
                    new_groups.append(groups[g])

                item.lesson.teachers = new_teachers
                item.lesson.rooms = new_rooms
                item.lesson.groups = new_groups
                res.append(item.lesson)

            print(f"all items {i}")
            print(f'Inserting {len(res)} items')
            db.add_all(res)
            await db.commit()
            print('Committed changes')
    except FileNotFoundError:
        print(f'File {__academic__}.json was not found.')
    except sqlalchemy.exc.IntegrityError as e:
        print(f'Error: {str(e)}')
        await db.rollback()
    except Exception as e:
        traceback.format_exception_only(Exception, e)
        await db.rollback()


async def bulk_insert_room(db: AsyncSession) -> None:
    try:
        async with db.begin():
            print(f'Rooms inserting')
            result = await db.execute(select(CorpsModel.name, CorpsModel.guid))
            rows = result.fetchall()

            corps = {}
            for row in rows:
                corps[row[0]] = row[1]

            res = []
            with open(f'{getcwd()}/parsing/schedule/rooms/rooms.json', 'r', encoding='utf-8') as fp:
                dict_json = json.loads(fp.read().replace("'", '\''))
                for room in dict_json['rooms']:
                    res.append(RoomModel(
                        number=room['number'],
                        corps_guid=corps[room['corps']]
                    ))

            print(f'Inserting {len(res)} items')
            db.add_all(res)
            await db.commit()
            print('Committed changes')
    except FileNotFoundError:
        print(f'File rooms.json was not found.')
    except sqlalchemy.exc.IntegrityError as e:
        print(f'Error: {str(e)}')
        await db.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        await db.rollback()


async def bulk_insert_corps(db: AsyncSession) -> None:
    try:
        async with db.begin():
            print(f'Corps inserting')
            buf = set()
            with open(f'{getcwd()}/parsing/schedule/rooms/rooms.json', 'r', encoding='utf-8') as fp:
                print(f'Filename: rooms.json')
                dict_json = json.loads(fp.read().replace("'", '\''))
                for corps in dict_json['corps']:
                    buf.add(corps['name'])

            res = [CorpsModel(name=item) for item in buf]
            print(f'Inserting {len(res)} items')
            db.add_all(res)
            await db.commit()
            print('Committed changes')
    except FileNotFoundError:
        print(f'File {getcwd()}/rooms/rooms.jsonn was not found.')
    except sqlalchemy.exc.IntegrityError as e:
        print(f'Error: {str(e)}')
        await db.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        await db.rollback()


async def bulk_insert_teachers(db: AsyncSession) -> None:
    try:
        async with db.begin():
            print(f'Teachers inserting')
            teachers = set()
            with open(f'{getcwd()}/parsing/schedule/teachers/TeachersFullname.json', 'r', encoding='utf-8') as fp:
                dict_json = json.loads(fp.read().replace("'", '\''))
                for fullname in dict_json['teachers_fullname']:
                    teachers.add(fullname)

            res = []
            for teacher in teachers:
                buffer = teacher.split()
                if len(buffer) == 2:
                    shortname = buffer[0] + " " + buffer[1][0] + "."
                else:
                    shortname = buffer[0] + " " + buffer[1][0] + "." + buffer[2][0] + "."
                res.append(TeacherModel(
                    online_url=None,
                    alt_online_url=None,
                    trans=[TeacherTranslateModel(
                        name=shortname,
                        fullname=teacher,
                        lang='ru'
                    )]
                ))

            print(f'Inserting {len(res)} items')
            db.add_all(res)
            await db.commit()
            print('Committed changes')
    except FileNotFoundError:
        print(f'File TeachersFullname.json was not found.')
    except sqlalchemy.exc.IntegrityError as e:
        print(f'Error: {str(e)}')
        await db.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        await db.rollback()


async def bulk_translated_teachers(db: AsyncSession, langs: list[str]):
    try:
        teachers = await db.execute(select(TeacherModel))
        teachers = teachers.scalars().unique().all()
        await translate_teachers(db, teachers, langs)
        print(f'Inserting {len(teachers)} items')
        await db.commit()
        print('Committed changes')
    except sqlalchemy.exc.IntegrityError as e:
        print(f'Error: {str(e)}')
        await db.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        await db.rollback()


async def bulk_translated_schedule(db: AsyncSession, langs: list[str]):
    try:
        lessons = await db.execute(select(LessonModel))
        lessons = lessons.scalars().unique().all()
        await translate_lessons(db, lessons, langs)
        print(f'Inserting {len(lessons)} items')
        await db.commit()
        print('Committed changes')
    except sqlalchemy.exc.IntegrityError as e:
        print(f'Error: {str(e)}')
        await db.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        await db.rollback()
