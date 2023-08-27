from collections.abc import Iterable
from typing import Literal

from pydantic import validator

from .base import BaseModel


class Priority(BaseModel):
    stage: Literal["early", "standard", "late"] = "standard"

    before: set[str] = set()
    after: set[str] = set()

    @validator("before", "after")
    def convert_fields(cls, value: Iterable[str]):
        return set(value)


PrioritySentinel = Priority()
