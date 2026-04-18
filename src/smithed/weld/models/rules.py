import logging
from typing import Annotated, Literal

from pydantic import BeforeValidator, Field

from .validators import normalize_type


from .base import BaseModel
from .conditions import Condition, ConditionInverted, ConditionPackCheck  # noqa: F401
from .priority import Priority
from .sources import Source

logger = logging.getLogger(__name__)


class BaseRule(BaseModel):
    target: str
    conditions: list[Condition] = []
    priority: Priority | None = None


class AdditiveRule(BaseRule):
    source: Source


class MergeRule(AdditiveRule):
    type: Literal["weld:merge", "smithed:merge", "merge"]


class AppendRule(AdditiveRule):
    type: Literal["weld:append", "smithed:append", "append"]


class PrependRule(AdditiveRule):
    type: Literal["weld:prepend", "smithed:prepend", "prepend"]


class InsertRule(AdditiveRule):
    type: Literal["weld:insert", "smithed:insert", "insert"]
    index: int


class ReplaceRule(AdditiveRule):
    type: Literal["weld:replace", "smithed:replace", "replace"]


class RemoveRule(BaseRule):
    type: Literal["weld:remove", "smithed:remove", "remove"]


PureRule = Annotated[
    MergeRule | AppendRule | PrependRule | InsertRule | ReplaceRule | RemoveRule,
    Field(discriminator="type"),
]
Rule = Annotated[PureRule, BeforeValidator(normalize_type)]


# BaseRule.model_rebuild()
# AdditiveRule.model_rebuild()
# MergeRule.model_rebuild()
# AppendRule.model_rebuild()
# PrependRule.model_rebuild()
# InsertRule.model_rebuild()
# ReplaceRule.model_rebuild()
# RemoveRule.model_rebuild()
