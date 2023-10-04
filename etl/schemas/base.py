import json
from typing import Union

from pydantic import BaseModel


class Base(BaseModel):
    def model_dump_redis(self):
        json_obj = self.model_dump_json()
        return json_obj.replace('true', '"true"').replace('false', '"false"')

    @classmethod
    def model_validate_redis(cls, model: Union[str, bytes]):
        try:
            model = model.decode('utf-8')
            if not isinstance(model, str):
                raise TypeError('model must be a string')
            obj = model.replace('"true"', 'true').replace('"false"', 'false')
            return cls(**json.loads(obj))
        except Exception as e:
            print(f"Error obj: {obj}")
            raise e
