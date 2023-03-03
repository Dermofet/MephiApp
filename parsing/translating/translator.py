import json
import os
import sys

sys.path.append("..")
from pool import Pool
from task import TranslatePutTask

import parsing
from parsing.parsers.schedule_parser import ScheduleParser

API_PREFIX = "http://127.0.0.1:8000/api/2.0"


def translate_schedule(lang: str):
    res = []
    parser = ScheduleParser()
    i = 1
    print(f"Language - {lang}")
    for academic in parser.getAcademicTypes():
        try:
            with open(f'{os.pardir}\\parsing\\schedule\\{academic[0]}.json', 'r', encoding='utf-8') as fp:
                print(f'    Filename: {academic[0]}.json')
                dict_json = json.loads(fp.read().replace("'", '\''))
                for course in dict_json['courses']:
                    for group in course['groups']:
                        for day in group['schedule']:
                            for lesson in day['lessons']:
                                for lesson_var in lesson['lesson']:
                                    if len(lesson_var['teacher_name']) > 0:
                                        for teacher in lesson_var['teacher_name']:
                                            _lesson_ = {
                                                "time_start": lesson['time_start'],
                                                "time_end": lesson['time_end'],
                                                "dot": lesson_var['dot'],
                                                "weeks": lesson_var['weeks'],
                                                "day": day['day'],
                                                "date_start": lesson_var['date_start'],
                                                "date_end": lesson_var['date_end'],
                                                "type": lesson_var['lesson_type'],
                                                "name": lesson_var['lesson_name'],
                                                "subgroup": lesson_var['subgroup'],
                                                "group": group['name'],
                                                "course": course['name'],
                                                "room": lesson_var['room'],
                                                "academic": dict_json['name'],
                                                "teacher_name": teacher,
                                                "lang": lang,
                                            }
                                            res.append(TranslatePutTask(tid=i,
                                                                        url=API_PREFIX + '/lesson-translated',
                                                                        getId_url=API_PREFIX + '/lessons',
                                                                        data=_lesson_,
                                                                        description='Lesson PUT',
                                                                        lang=lang,
                                                                        src_lang="ru"))
                                            i += 1
                                    else:
                                        _lesson_ = {
                                            "time_start": lesson['time_start'],
                                            "time_end": lesson['time_end'],
                                            "dot": lesson_var['dot'],
                                            "weeks": lesson_var['weeks'],
                                            "day": day['day'],
                                            "date_start": lesson_var['date_start'],
                                            "date_end": lesson_var['date_end'],
                                            "type": lesson_var['lesson_type'],
                                            "name": lesson_var['lesson_name'],
                                            "subgroup": lesson_var['subgroup'],
                                            "group": group['name'],
                                            "course": course['name'],
                                            "room": lesson_var['room'],
                                            "academic": dict_json['name'],
                                            "teacher_name": None,
                                            "lang": lang,
                                        }
                                        res.append(TranslatePutTask(tid=i,
                                                                    url=API_PREFIX + '/lesson-translated',
                                                                    getId_url=API_PREFIX + '/lessons',
                                                                    data=_lesson_,
                                                                    description='Lesson PUT',
                                                                    lang=lang,
                                                                    src_lang="ru"))
                                        i += 1
        except FileNotFoundError as err:
            print(f'File {academic[0]}.json was not found.')
    return res


async def start_parse_trans(pool: Pool):
    for lang in parsing.config.LANGS:
        if lang == "ru":
            continue

        tasks = translate_schedule(lang)
        for task in tasks:
            await pool.put(task)
    pool.start()
    await pool.join()
    await pool.stop()
