from typing import Literal

from smithed.type import JsonType

from .base import BaseModel


class ReferenceSource(BaseModel):
    type: Literal["reference", "smithed:reference"]
    path: str


class ValueSource(BaseModel):
    type: Literal["value", "smithed:value"] = "smithed:value"
    value: JsonType


Source = ValueSource | ReferenceSource
