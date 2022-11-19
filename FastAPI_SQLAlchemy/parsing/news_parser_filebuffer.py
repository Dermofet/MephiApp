# import requests
# from lxml import etree
# import json
# import os
# import re
# import html2text
#
# from .config import settings
# import FastAPI_SQLAlchemy.parsing.schedule_parser as sp
#
#
# def get_OneUrlNews(url):
#     text = sp.getText(url)
#     tree = etree.HTML(text)
#     container = tree.xpath("//div[@class='view-content']")[0]
#     with open(settings.BUFFER_2, mode='a', encoding='utf-8') as fp:
#         for element in container:
#             fp.write(settings.HOST_URL + element[0][0][0].attrib['href'] + "\n")
#     if len(tree.xpath("//li[@class='pager-next']")) != 0:
#         return settings.HOST_URL + tree.xpath("//li[@class='pager-next']")[0][0].attrib['href']
#     else:
#         return None
#
#
# def get_urlNews(url):
#     while url is not None:
#         print("   {}".format(url))
#         url = get_OneUrlNews(url)
#
#
# def get_urlPage(url):
#     text = sp.getText(url)
#     tree = etree.HTML(text)
#     with open(settings.BUFFER_1, mode='a', encoding='utf-8') as fp:
#         fp.write(url + "\n")
#     if len(tree.xpath("//li[@class='pager-next']")) != 0:
#         return settings.HOST_URL + tree.xpath("//li[@class='pager-next']")[0][0].attrib['href']
#     else:
#         return None
#
#
# def get_urlPages(url):
#     while url is not None:
#         print("   {}".format(url))
#         url = get_urlPage(url)
#
#
# def parse_preview(url):
#     text = sp.getText(url)
#     tree = etree.HTML(text)
#     print(tree.xpath("//div[@class='view-content']"))
#     container = tree.xpath("//div[@class='view-content']")[0]
#     res = []
#     print(len(container))
#     for element in container:
#         img = {"img_url": element.xpath(".//img")[0].xpath(".//@src")[0]}
#         print(img)
#         date = {"date": element.xpath(".//span[@class='date-display-single']")[0].text}
#         print(date)
#         text = {"text": element.xpath(".//a")[1].text}
#         print(text)
#         res.append({"img_url": element.xpath(".//img")[0].xpath(".//@src")[0],
#                     "date": element.xpath(".//span[@class='date-display-single']")[0].text,
#                     "text": element.xpath(".//a")[1].text
#                     })
#         print(res)
#     return res
#
#
# def parse_WebPage(url):
#     text = sp.getText(url)
#     tree = etree.HTML(text)
#     res = {"title": tree.xpath("//h1[@id='page-title']")[0].text}
#     container = tree.xpath("//div[@class='node node-news clearfix']")[0]
#     content = container.xpath(".//div[@class='field-item even']")[0]
#
#     res["date"] = container[0][0].text + ' ' + container[0][1].text + ' ' + container[0][2].text
#     res_text = ""
#     for paragraph in content:
#         text = etree.tostring(paragraph).decode('utf-8')
#         text = re.sub(r'<em>.*?</em>', '', text)
#         text = html2text.html2text(text)
#         text = text.replace('### ', '').replace('\n\n', '\n')
#         for word in re.findall(r'\*\*.*? ', text):
#             need_word = word[2:][:-1]
#             pos = text.find(word)
#             string1 = text[:pos]
#             string2 = text[pos + len(word):]
#             if need_word[:1].isdigit() is True:
#                 text = string1 + need_word + ' ' + string2
#             else:
#                 text = string1 + need_word + string2
#         text = text.replace("**", ' ')
#         text = re.sub(r'\n(\s+)\n', '\n\n', text)
#         text = text.replace("\n\n", "##").replace("\n", " ").replace("##", "\n\n")
#         res_text += text
#
#     res["images_url"] = []
#     for url in re.findall(r'!\[]\(.*?\)', res_text):
#         res["images_url"].append(settings.HOST_URL + url[4:][:-1])
#     res_text = res_text.replace("_", " ")
#     res_text = re.sub(r'!\[]\(.*?\)', '', res_text)
#     res["text"] = res_text
#     return res
#
#
# def parse_previews(pathToWrite):
#     i = 1
#     j = 1
#     try:
#         print("- Start parsing previews -")
#         with open(settings.BUFFER_1, 'r', encoding='utf-8') as fp:
#             page_url = fp.readline()
#             while len(page_url) > 0:
#                 print("current page: {}".format(j))
#                 res = parse_preview(page_url)
#                 print(res)
#                 for preview in res:
#                     with open(pathToWrite + str(j) + ".json", 'w', encoding='utf-8') as fp_json:
#                         json.dump(preview, fp=fp_json, ensure_ascii=False, indent=3)
#                         j += 1
#                 i += 1
#                 page_url = fp.readline()
#     except IndexError as err:
#         print(err)
#
#         if os.path.exists(pathToWrite + str(i) + ".json"):
#             os.remove(pathToWrite + str(i) + ".json")
#         i -= 1
#         print("-!!! An exception occurred !!!-")
#
#     print("- Pages were parsed: {} -".format(i))
#     print("- Previews were parsed: {} -".format(j))
#     print("- Successful parsing -\n")
#
#
# def parse_news(pathToWrite):
#     i = 1
#     try:
#         print("- Start parsing pages -")
#         with open(settings.BUFFER_2, 'r', encoding='utf-8') as fp:
#             page_url = fp.readline()
#             while len(page_url) > 0:
#                 print("   current page: {}".format(i))
#                 with open(pathToWrite + str(i) + ".json", 'w', encoding='utf-8') as fp_json:
#                     json.dump(parse_WebPage(page_url), fp=fp_json, ensure_ascii=False, indent=3)
#                     i += 1
#                 page_url = fp.readline()
#     except IndexError as err:
#         print(err)
#
#         if os.path.exists(pathToWrite + str(i) + ".json"):
#             os.remove(pathToWrite + str(i) + ".json")
#         i -= 1
#         print("-!!! An exception occurred !!!-")
#
#     print("- News were parsed: {} -".format(i))
#     print("- Successful parsing -\n")
#
#
# def parse_category(category: tuple):
#     if not os.path.exists("./FastAPI_SQLAlchemy/parsing/news/" + str(category[0])):
#         print("- Can't find news directory <{}>. Creating directory -".format(str(category[0])))
#         os.makedirs("./FastAPI_SQLAlchemy/parsing/news/" + str(category[0]))
#     if not os.path.exists("./FastAPI_SQLAlchemy/parsing/preview/" + str(category[0])):
#         print("- Can't find preview directory <{}>. Creating directory -".format(str(category[0])))
#         os.makedirs("./FastAPI_SQLAlchemy/parsing/preview/" + str(category[0]))
#
#     print("- Parsing pages' urls -")
#     get_urlPages(category[1])
#     parse_previews("./FastAPI_SQLAlchemy/parsing/preview/{}/".format(category[0]))
#     print("- Parsing news' urls -")
#     get_urlNews(category[1])
#     parse_news("./FastAPI_SQLAlchemy/parsing/news/{}/".format(category[0]))
#
#     os.remove(settings.BUFFER_1)
#     os.remove(settings.BUFFER_2)
#
#
# def parse():
#     for category in settings.NEWS_CAT_URLS.items():
#         print("- Parse category: {} -".format(category[0]))
#         parse_category(category)
