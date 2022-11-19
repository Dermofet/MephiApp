import time

import html2text
import lxml.html
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from lxml import etree
import json
import os
from .config import settings

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/104.0.0.0 Safari/537.36'}
DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']


def getText(url):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session.get(url, headers=headers).text


def getAcademicTypes():
    res = []
    text = getText(settings.URL_ALL_SCHEDULE)
    tree = etree.HTML(text)
    container = tree.xpath("//ul[@class='nav nav-tabs btn-toolbar']/li")
    for item in container:
        res.append(item[0].text.replace('\n', ''))
    return res


def getAcademicGroupList(name, url):
    text = getText(url)
    tree = etree.HTML(text)
    container = tree.xpath("//ul[@class='nav nav-tabs btn-toolbar']/li")
    res = {}
    for item in container:
        if item[0].text.replace('\n', '') == name:
            res["name"] = item[0].text.replace('\n', '')
            res.update(getGroupList(settings.URL_HOME_MEPHI + item[0].attrib['href']))
    return res


def getGroupList(url):
    text = getText(url)
    tree = etree.HTML(text)
    items_div = tree.xpath("//div[@class='col-sm-2']")
    res = {"courses": []}
    for item in items_div:
        if len(item) > 1:
            res["courses"].append({"name": item[0].text.replace('\n', ''),
                                   "groups": []})
            groups = res["courses"][len(res["courses"]) - 1]["groups"]
            for node in item[1]:
                groups.append({"name": node.text.replace('\n', ''),
                               "url": settings.URL_HOME_MEPHI + node.attrib['href']})
            res["courses"][len(res["courses"]) - 1]["groups"] = groups
    return res


def getTeachersFullname():
    text = getText(settings.URL_TEACHERS_SCHEDULE)
    tree = etree.HTML(text)
    categories = []
    for item in tree.xpath("//ul[@class='pagination']")[0]:
        categories.append(settings.URL_HOME_MEPHI + item[0].attrib['href'])

    res = {"teachers_fullname": []}
    for category in categories:
        text = getText(category)
        tree = etree.HTML(text)
        for item in tree.xpath("//a[@class='list-group-item']"):
            res["teachers_fullname"].append(item.text.replace('\n', ''))
    return res


def setTeachersFullname(filename, obj, mode, encoding, indent, ensure_ascii):
    with open(filename, mode=mode, encoding=encoding) as fp:
        json.dump(obj, fp=fp, ensure_ascii=ensure_ascii, indent=indent)


def getGroupSchedule(url):
    text = getText(url)
    tree = etree.HTML(text)
    schedule = {}
    i = 0
    for day in tree.xpath("//div[@class='list-group']"):
        schedule[DAYS[i]] = []

        j = 0
        for node in day:
            schedule[DAYS[i]].append({})
            time = node[0].text.replace('\n', '').split(' — ')
            schedule[DAYS[i]][j]['time_start'] = time[0]
            schedule[DAYS[i]][j]['time_end'] = time[1]

            schedule[DAYS[i]][j]["lessons"] = []

            for elem in node[1]:
                schedule_elem = {}
                if len(elem.xpath(".//div[@class='pull-right']")[0]) == 1:
                    schedule_elem['dot'] = True
                    schedule_elem['cabinet'] = None
                else:
                    schedule_elem['dot'] = False
                    schedule_elem['cabinet'] = elem.xpath(".//div[@class='pull-right']")[0][1].text

                if len(elem.xpath(".//div[@class='label label-default label-lesson']")) == 1:
                    schedule_elem['lesson_type'] = elem.xpath(".//div[@class='label label-default label-lesson']")[0] \
                        .text.replace('\n', '')
                else:
                    schedule_elem['lesson_type'] = None

                weeks = elem.xpath(".//span")
                for a in weeks:
                    a = a.xpath("./@class")[0].replace('\n', '')
                    if a == "lesson-square lesson-square-0":
                        schedule_elem["weeks"] = "еженед"
                    elif a == "lesson-square lesson-square-1":
                        schedule_elem["weeks"] = "нечет"
                    elif a == "lesson-square lesson-square-2":
                        schedule_elem["weeks"] = "чет"

                strings = [v.replace('\n', '').replace(',', '') for v in elem.xpath(".//div/following-sibling::text()")
                           if len(v.replace('\n', '').replace(',', '')) > 0]
                schedule_elem['lesson_name'] = None if len(strings) < 1 else strings[0]
                schedule_elem['subgroup'] = None if len(strings) < 2 else strings[1]

                schedule_elem['teacher_name'] = []
                schedule_elem['teacher_fullname'] = []
                schedule_elem['online_url'] = []
                schedule_elem['alt_online_url'] = []
                for teacher in elem.xpath(".//span[@class='text-nowrap']"):
                    schedule_elem['teacher_name'].append(teacher[0].text.replace('\n', '').replace(' ', ' '))
                    # schedule_elem['teacher_fullname'].append("")
                    # schedule_elem['online_url'].append("")
                    # schedule_elem['alt_online_url'].append("")

                schedule_elem["date_start"] = None
                schedule_elem["date_end"] = None
                if len(elem.xpath(".//span[@class='lesson-dates']")) != 0:
                    date = elem.xpath(".//span[@class='lesson-dates']")[0].text.replace('\n', '').split(' — ')
                    if len(date) == 1:
                        date = date[0].split(', ')
                    if len(date) == 1:
                        schedule_elem["date_start"] = date[0].replace('(', '').replace(')', '')
                        schedule_elem["date_end"] = None
                    else:
                        schedule_elem["date_start"] = date[0].replace('(', '').replace(')', '')
                        schedule_elem["date_end"] = date[1].replace('(', '').replace(')', '')

                schedule[DAYS[i]][j]["lessons"].append(schedule_elem)
            j += 1

        i += 1
    return schedule


def setInfoToFile(dict_json, filename, mode, encoding, indent, ensure_ascii):
    dict_dump = {"name": filename.split(".")[0],
                 "courses": []}
    i = 0
    for course in dict_json["courses"]:
        dict_dump["courses"].append({"name": course["name"].split()[0],
                                     "groups": []})
        for group in course["groups"]:
            print("   " + group["name"])
            dict_dump["courses"][i]["groups"].append({"name": group["name"],
                                                      "lessons": getGroupSchedule(group["url"])})
        i += 1

    with open(filename, mode, encoding=encoding) as fp:
        json.dump(dict_dump, fp=fp, indent=indent, ensure_ascii=ensure_ascii)


def parse_schedule():
    for academic in ['Специалитет']:
        print(academic + ":")
        groups_list = getAcademicGroupList(academic, url=settings.URL_ALL_SCHEDULE)
        setInfoToFile(groups_list, "FastAPI_SQLAlchemy/parsing/schedule/" + academic + ".json", mode='w',
                      encoding='utf-8', indent=3, ensure_ascii=False)


def parse_teachers_fullname():
    setTeachersFullname("FastAPI_SQLAlchemy/parsing/schedule/TeachersFullname.json", obj=getTeachersFullname(),
                        mode='w', encoding='utf-8', indent=3, ensure_ascii=False)
