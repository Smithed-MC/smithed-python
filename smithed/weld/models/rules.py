from __future__ import annotations

import logging
from typing import Annotated, Literal

from pydantic import Field

from .base import BaseModel
from .conditions import Condition
from .priority import Priority
from .sources import Source

logger = logging.getLogger(__name__)


class BaseRule(BaseModel):
    target: str
    conditions: list[Condition] = []
    priority: Priority | None = None


class AdditiveRule(BaseRule):
    source: Source = Field(..., discriminator="type")


class MergeRule(AdditiveRule):
    type: Literal["merge", "smithed:merge"]


class AppendRule(AdditiveRule):
    type: Literal["append", "smithed:append"]


class PrependRule(AdditiveRule):
    type: Literal["prepend", "smithed:prepend"]


class InsertRule(AdditiveRule):
    type: Literal["insert", "smithed:insert"]
    index: int


class ReplaceRule(AdditiveRule):
    type: Literal["replace", "smithed:replace"]


class RemoveRule(BaseRule):
    type: Literal["remove", "smithed:remove"]


Rule = Annotated[
    MergeRule | AppendRule | PrependRule | InsertRule | ReplaceRule | RemoveRule,
    Field(..., discriminator="type"),
]
