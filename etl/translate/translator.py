from typing import List, Union
import requests

from etl.translate.error import InvalidMaxLengthError

NoneType = type(None)

class YandexTranslator:
    iam_token: str
    folder_id: str

    def __init__(
        self,
        iam_token: str,
        folder_id: str
    ) -> None:
        self.iam_token = iam_token
        self.folder_id = folder_id

    def translate(self, source: str, target: str, text: Union[str, List[Union[str, NoneType]]]) -> List[str]:
        text = text if isinstance(text, list) else [text]

        for i in range(len(text)):
            if text[i] is None:
                text[i] = ""

        text_len = len("".join(text))
        print(text_len)
        if text_len > 10000:
            raise InvalidMaxLengthError(10000, text_len)

        body = {
            "targetLanguageCode": target,
            "sourceLanguageCode": source,
            "texts": text,
            "folderId": self.folder_id,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.iam_token}",
        }

        response = requests.post(
            'https://translate.api.cloud.yandex.net/translate/v2/translate',
            json=body,
            headers=headers
        )

        if response.status_code != 200:
            raise Exception(f"{response.status_code} : {response.text}")

        return [
            t.get('text', None)
            for t in response.json()["translations"]
        ]



