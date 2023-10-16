import requests
from lxml import etree
import json
import os
import re
import html2text

from .config import settings
import FastAPI_SQLAlchemy.parsing.schedule_parser as sp


def get_urlNews(url):
    text = sp.getText(url)
    tree = etree.HTML(text)
    container = tree.xpath("//div[@class='view-content']")[0]
    res_urlNews = [
        settings.HOST_URL + element[0][0][0].attrib['href']
        for element in container
    ]
    if len(tree.xpath("//li[@class='pager-next']")) != 0:
        return res_urlNews + get_urlNews(settings.HOST_URL + tree.xpath("//li[@class='pager-next']")[0][0].attrib['href'])
    else:
        return res_urlNews


def get_urlPages(url):
    text = sp.getText(url)
    tree = etree.HTML(text)
    res_urlPages = [url]
    if len(tree.xpath("//li[@class='pager-next']")) != 0:
        return res_urlPages + get_urlPages(settings.HOST_URL + tree.xpath("//li[@class='pager-next']")[0][0].attrib['href'])
    else:
        return res_urlPages


def parse_preview(url):
    text = sp.getText(url)
    tree = etree.HTML(text)
    container = tree.xpath("//div[@class='view-content']")[0]
    return [
        {
            "img_url": element.xpath(".//img")[0].xpath(".//@src")[0],
            "date": element.xpath(".//span[@class='date-display-single']")[
                0
            ].text,
            "text": element.xpath(".//a")[1].text,
        }
        for element in container
    ]


def parse_WebPage(url):
    text = sp.getText(url)
    tree = etree.HTML(text)
    res = {"title": tree.xpath("//h1[@id='page-title']")[0].text}
    container = tree.xpath("//div[@class='node node-news clearfix']")[0]
    content = container.xpath(".//div[@class='field-item even']")[0]

    res[
        "date"
    ] = f'{container[0][0].text} {container[0][1].text} {container[0][2].text}'
    res_text = ""
    for paragraph in content:
        text = etree.tostring(paragraph).decode('utf-8')
        text = re.sub(r'<em>.*?</em>', '', text)
        text = html2text.html2text(text)
        text = text.replace('### ', '').replace('\n\n', '\n')
        for word in re.findall(r'\*\*.*? ', text):
            need_word = word[2:][:-1]
            pos = text.find(word)
            string1 = text[:pos]
            string2 = text[pos + len(word):]
            if need_word[:1].isdigit() is True:
                text = string1 + need_word + ' ' + string2
            else:
                text = string1 + need_word + string2
        text = text.replace("**", ' ')
        text = re.sub(r'\n(\s+)\n', '\n\n', text)
        text = text.replace("\n\n", "##").replace("\n", " ").replace("##", "\n\n")
        res_text += text

    res["images_url"] = []
    for url in re.findall(r'!\[]\(.*?\)', res_text):
        res["images_url"].append(settings.HOST_URL + url[4:][:-1])
    res_text = res_text.replace("_", " ")
    res_text = re.sub(r'!\[]\(.*?\)', '', res_text)
    res["text"] = res_text
    return res


def parse_previews(URLs, pathToWrite):
    i = 1
    j = 1
    try:
        print("- Start parsing previews -")
        for page_url in URLs:
            print(f"current page: {j}")
            res = parse_preview(page_url)
            for preview in res:
                with open(pathToWrite + str(j) + ".json", 'w', encoding='utf-8') as fp:
                    json.dump(preview, fp=fp, ensure_ascii=False, indent=3)
                    j += 1
            i += 1
    except IndexError as err:
        print(err)

        if os.path.exists(pathToWrite + str(i) + ".json"):
            os.remove(pathToWrite + str(i) + ".json")
        i -= 1
        print("-!!! An exception occurred !!!-")

    print(f"- Pages were parsed: {i} -")
    print(f"- Previews were parsed: {j} -")
    print("- Successful parsing -\n")


def parse_news(URLs, pathToWrite):
    i = 1
    try:
        print("- Start parsing pages -")
        for page_url in URLs:
            print(f"   current page: {i}")
            with open(pathToWrite + str(i) + ".json", 'w', encoding='utf-8') as fp:
                json.dump(parse_WebPage(page_url), fp=fp, ensure_ascii=False, indent=3)
                i += 1
    except IndexError as err:
        print(err)

        if os.path.exists(pathToWrite + str(i) + ".json"):
            os.remove(pathToWrite + str(i) + ".json")
        i -= 1
        print("-!!! An exception occurred !!!-")

    print(f"- News were parsed: {i} -")
    print("- Successful parsing -\n")


def parse_category(category: tuple):
    if not os.path.exists(
        f"./FastAPI_SQLAlchemy/parsing/news/{str(category[0])}"
    ):
        os.makedirs(f"./FastAPI_SQLAlchemy/parsing/news/{str(category[0])}")
    if not os.path.exists(
        f"./FastAPI_SQLAlchemy/parsing/preview/{str(category[0])}"
    ):
        os.makedirs(f"./FastAPI_SQLAlchemy/parsing/preview/{str(category[0])}")
    parse_previews(
        get_urlPages(category[1]),
        f"./FastAPI_SQLAlchemy/parsing/preview/{category[0]}/",
    )
    parse_news(
        get_urlNews(category[1]),
        f"./FastAPI_SQLAlchemy/parsing/news/{category[0]}/",
    )


def parse():
    for category in settings.NEWS_CAT_URLS.items():
        print(f"- Parse category: {category[0]} -")
        parse_category(category)
