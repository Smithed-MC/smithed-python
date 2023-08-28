import warnings
from collections.abc import Iterable
from typing import Literal

from pydantic import validator

from .base import BaseModel


class Priority(BaseModel):
    stage: Literal["early", "standard", "late"] = "standard"
    default: int = 0

    before: set[str] = set()
    after: set[str] = set()

    @validator("default")
    def warn_default(cls, value: int):
        warnings.warn("Default priority is deprecated, `stage` instead")
        return 0

    @validator("before", "after")
    def convert_fields(cls, value: Iterable[str]):
        return set(value)


PrioritySentinel = Priority()
