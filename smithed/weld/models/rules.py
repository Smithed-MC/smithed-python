from __future__ import annotations

import logging
from typing import Annotated, Literal

from pydantic import Field, validator

from .base import BaseModel
from .conditions import Condition
from .priority import Priority
from .sources import Source

logger = logging.getLogger(__name__)


class BaseRule(BaseModel):
    type: str
    target: str
    conditions: list[Condition] = []
    priority: Priority | None = None

    @validator("type")
    def fix_type(cls, value: str):
        if value.startswith("smithed:"):
            return value.replace("smithed:", "weld:")
        return value


class AdditiveRule(BaseRule):
    source: Source


class MergeRule(AdditiveRule):
    type: Literal["merge", "weld:merge", "smithed:merge"]


class AppendRule(AdditiveRule):
    type: Literal["append", "weld:append", "smithed:append"]


class PrependRule(AdditiveRule):
    type: Literal["prepend", "weld:prepend", "smithed:prepend"]


class InsertRule(AdditiveRule):
    type: Literal["insert", "weld:insert", "smithed:insert"]
    index: int


class ReplaceRule(AdditiveRule):
    type: Literal["replace", "weld:replace", "smithed:replace"]


class RemoveRule(BaseRule):
    type: Literal["remove", "weld:remove", "smithed:remove"]


Rule = Annotated[
    MergeRule | AppendRule | PrependRule | InsertRule | ReplaceRule | RemoveRule,
    Field(..., discriminator="type"),
]
