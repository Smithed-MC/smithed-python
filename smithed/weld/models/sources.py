from typing import Any, Literal

from .base import BaseModel


class ReferenceSource(BaseModel):
    type: Literal["reference", "smithed:reference"]
    path: str


class ValueSource(BaseModel):
    type: Literal["value", "smithed:value"] = "smithed:value"
    value: Any


Source = ValueSource | ReferenceSource
