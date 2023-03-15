import json
import sys
import traceback
from os import getcwd
from typing import Optional

import sqlalchemy
from parsers.schedule_parser import ScheduleParser
from sqlalchemy import join, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models.academic import AcademicModel
from backend.database.models.association_tables import AT_lesson_group, AT_lesson_room, AT_lesson_teacher
from backend.database.models.corps import CorpsModel
from backend.database.models.group import GroupModel
from backend.database.models.lesson import LessonModel
from backend.database.models.lesson_translate import LessonTranslateModel
from backend.database.models.room import RoomModel
from backend.database.models.teacher import TeacherModel
from backend.database.models.teacher_translate import TeacherTranslateModel


async def bulk_insert_academic(db: AsyncSession) -> None:
    try:
        async with db.begin():
            parser = ScheduleParser()
            res = [AcademicModel(name=academic[0]) for academic in parser.getAcademicTypes()]
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
    try:
        async with db.begin():
            print(f'Groups inserting')
            academics = await db.execute(select([AcademicModel.name, AcademicModel.guid]))
            academics = academics.scalars().all()
            a = {}
            for name, guid in academics:
                a[name] = guid

            res = []
            parser = ScheduleParser()
            for academic in parser.getAcademicTypes():
                with open(f'{getcwd()}/parsing/schedule/{academic[0]}.json', 'r', encoding='utf-8') as fp:
                    dict_json = json.loads(fp.read().replace("'", '\''))
                    for course in dict_json['courses']:
                        for group in course['groups']:
                            res.append(GroupModel(
                                name=group['name'],
                                course=course['name'],
                                academic_guid=a[dict_json['name']]
                            ))
            print(f'Inserting {len(res)} items')
            db.add_all(res)
            await db.commit()
            print('Committed changes')
    except FileNotFoundError:
        print(f'File {academic[0]}.json was not found.')
    except sqlalchemy.exc.IntegrityError as e:
        print(f'Error: {str(e)}')
        await db.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        await db.rollback()


async def bulk_insert_schedule(db: AsyncSession) -> None:
    try:
        async with db.begin():
            print(f'Schedule inserting')
            groups_sc = await db.execute(select(GroupModel))
            groups_sc = groups_sc.scalars().all()
            groups = {}
            for group in groups_sc:
                groups[group.name] = group

            room_sc = await db.execute(select(RoomModel))
            room_sc = room_sc.scalars().all()
            rooms = {}
            for room in room_sc:
                rooms[room.number] = room

            teacher_sc = await db.execute(select([TeacherTranslateModel.name, TeacherModel])
                                               .select_from(join(TeacherTranslateModel.name,
                                                                 TeacherTranslateModel.teacher_guid == TeacherModel.guid)))
            teacher_sc = teacher_sc.scalars().all()
            teachers = {}
            for name, teacher in teacher_sc:
                teachers[name] = teacher

            res_lessons = set()
            parser = ScheduleParser()
            for academic in parser.getAcademicTypes():
                with open(f'{getcwd()}/parsing/schedule/{academic[0]}.json', 'r', encoding='utf-8') as fp:
                    dict_json = json.loads(fp.read().replace("'", '\''))
                    for course in dict_json['courses']:
                        for group in course['groups']:
                            for day in group['schedule']:
                                for lesson in day['lessons']:
                                    for lesson_var in lesson['lesson']:
                                        res_lessons.add(LessonModel(
                                            time_start=lesson['time_start'],
                                            time_end=lesson['time_end'],
                                            dot=lesson_var['dot'],
                                            weeks=lesson_var['weeks'],
                                            day=day['day'],
                                            date_start=lesson_var['date_start'],
                                            date_end=lesson_var['date_end'],
                                            teachers=[teachers[teacher] for teacher in lesson_var['teacher_name']],
                                            groups=[groups[group]],
                                            room=[rooms[lesson_var['room']]],
                                            trans=LessonTranslateModel(
                                                name=lesson_var['lesson_name'],
                                                subgroup=lesson_var['subgroup'],
                                                lang='ru',
                                                type=lesson_var['lesson_type']
                                            )
                                        ))

            print(f'Inserting {len(res)} items')
            db.add_all(res)
            await db.commit()
            print('Committed changes')
    except FileNotFoundError:
        print(f'File {academic[0]}.json was not found.')
    except sqlalchemy.exc.IntegrityError as e:
        print(f'Error: {str(e)}')
        await db.rollback()
    except Exception as e:
        print(f'Error: {str(e)}')
        await db.rollback()


async def bulk_insert_room(db: AsyncSession) -> None:
    try:
        async with db.begin():
            print(f'Rooms inserting')
            corps_sc = await db.execute(select(CorpsModel.name, CorpsModel.guid))
            corps_sc = corps_sc.scalars().all()
            corps = {}
            for name, guid in corps_sc:
                corps[name] = guid

            res = []
            with open(f'{getcwd()}/parsing/rooms/rooms.json', 'r', encoding='utf-8') as fp:
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
        print(f'File {academic[0]}.json was not found.')
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
            res = []
            with open(f'{getcwd()}/parsing/rooms/rooms.json', 'r', encoding='utf-8') as fp:
                print(f'Filename: rooms.json')
                dict_json = json.loads(fp.read().replace("'", '\''))
                for corps in dict_json['corps']:
                    res.append(CorpsModel(name=corps['name']))

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


async def bulk_insert_teachers_fullname(db: AsyncSession) -> None:
    try:
        async with db.begin():
            print(f'Teachers isnserting')
            res = []
            with open(f'{getcwd()}\\teachers\\TeachersFullname.json', 'r', encoding='utf-8') as fp:
                dict_json = json.loads(fp.read().replace("'", '\''))
                for fullname in dict_json['teachers_fullname']:
                    buffer = fullname.split()
                    if len(buffer) == 2:
                        shortname = buffer[0] + " " + buffer[1][0] + "."
                    else:
                        shortname = buffer[0] + " " + buffer[1][0] + "." + buffer[2][0] + "."
                    res.append(TeacherModel(
                        online_url=None,
                        alt_online_url=None,
                        trans=[TeacherTranslateModel(
                            name=shortname,
                            fullname=fullname,
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
