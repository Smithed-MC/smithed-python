from typing import TypeVar

from pydantic import BaseModel as _BaseModel

T = TypeVar("T")


class BaseModel(_BaseModel):
    class Config:
        json_encoders = {dict: lambda v: list(v)}
