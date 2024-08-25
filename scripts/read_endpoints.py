import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, create_model

APP_DIR = Path(__file__).resolve(strict=True).parent.parent


class EndpointsV1(BaseModel):
    class Config:
        extra = "allow"

    description: None = Field(default=None, description="Model of endpoints generated from json")

    def __init__(__pydantic_self__, **data: Any) -> None:
        registered, not_registered = __pydantic_self__.filter_data(data)
        super().__init__(**registered)
        for k, v in not_registered.items():
            __pydantic_self__.__dict__[k] = v

    @classmethod
    def filter_data(cls, data):
        registered_attr = {}
        not_registered_attr = {}
        annots = cls.__annotations__
        for k, v in data.items():
            if k in annots:
                registered_attr[k] = v
            else:
                not_registered_attr[k] = v
        return registered_attr, not_registered_attr


class EndpointsV2(BaseModel):
    class Config:
        extra = "allow"

    description: None = Field(default=None, description="Model of endpoints generated from json")

    def __init__(__pydantic_self__, **data: Any) -> None:
        registered = __pydantic_self__.filter_data_v2(data)
        super().__init__(**registered)

    @classmethod
    def filter_data_v1(cls, data) -> dict:
        def pydantify(key, dataset):
            for k, v in dataset.items():
                if isinstance(v, dict):
                    v = pydantify(k, v)
                dataset[k] = (type(v), v)
            return create_model(key, **dataset)
        registered_attr = {}
        attr = pydantify("Endpoints", data)
        return registered_attr

    @classmethod
    def filter_data_v2(cls, data) -> dict:
        def pydantify(key, dataset):
            for k, v in dataset.items():
                if isinstance(v, dict):
                    dataset[k] = pydantify(k, v)
            return create_model(key, **dataset, __config__={"extra": "allow"})
        registered_attr = {}
        attr = pydantify("Endpoints", data)
        return registered_attr


def main(filename: str) -> None:
    with open(APP_DIR / "static" / filename) as json_file:
        data = json.load(json_file)
        print(EndpointsV1(**data))
        print(EndpointsV2(**data))


if __name__ == "__main__":
    main("v5_endpoints.json")
