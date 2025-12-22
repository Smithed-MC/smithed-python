import logging
from typing import Literal

from beet import ListOption
from pydantic import field_validator

from .base import BaseModel

logger = logging.getLogger("weld")


class Priority(BaseModel):
    stage: Literal["early", "standard", "late"] = "standard"
    default: int = 0

    before: ListOption[str] = ListOption()
    after: ListOption[str] = ListOption()

    @field_validator("before", "after")
    def convert_fields(cls, value: ListOption[str]):
        return ListOption(__root__=list(dict.fromkeys(value.entries())))
