from multipledispatch import dispatch

# from googletrans import Translator, constants
#
# translator = Translator()

from yandex.Translater import Translater

translator = Translater()

@dispatch(dict)
def translate(text: dict, dest='en'):
    if dest != 'ru':
        for key in text:
            text[key] = translate(text[key], dest=dest)
    return text


@dispatch(list)
def translate(text: list, dest='en'):
    if dest != 'ru':
        for i in range(0, len(text)):
            text[i - 1] = translate(text[i - 1], dest=dest)
    return text


@dispatch(str)
def translate(text: str, dest='en'):
    if dest != 'ru':
        res = ""
        for substr in tr_split(text, 5000):
            res += translator.translate(substr, dest=dest).text
        return res
    return text


def tr_split(text: str, length: int):
    if len(text) <= length:
        return [text]
    res = []
    for i in range(0, len(text) // length):
        res.append(text[i * length:(i + 1) * length])
    res.append(text[(len(text) // length)*length:])
    return res
