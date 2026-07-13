from typing import Any, Type

from pydantic import BaseModel
from sanic import json


def response_error(message: str, status: int = 400, **extra):
    body = {"error": message, **extra}
    return json(body, status=status)


def response_result(model_cls: Type[BaseModel], data: Any, status: int = 200):
    if isinstance(data, list):
        return json(
            [model_cls.model_validate(item).model_dump(mode="json") for item in data],
            status=status,
        )
    return json(model_cls.model_validate(data).model_dump(mode="json"), status=status)


def response_message(message: str, status: int = 200):
    return json({"message": message}, status=status)
