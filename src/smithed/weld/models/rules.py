import logging
from typing import Annotated, Literal

from pydantic import BeforeValidator, Field

from .validators import normalize_type
from .base import BaseModel
from .conditions import Condition, ConditionInverted, ConditionPackCheck  # noqa: F401
from .priority import Priority
from .sources import _Source, BroadSource, ValueSource

logger = logging.getLogger(__name__)


class BaseRule(BaseModel):
    target: str
    conditions: list[Condition] = []
    priority: Priority | None = None


class AdditiveRule[SourceT: _Source](BaseRule):
    source: SourceT


class MergeRule[SourceT: _Source](AdditiveRule[SourceT]):
    type: Literal["weld:merge", "smithed:merge", "merge"]


class AppendRule[SourceT: _Source](AdditiveRule[SourceT]):
    type: Literal["weld:append", "smithed:append", "append"]


class PrependRule[SourceT: _Source](AdditiveRule[SourceT]):
    type: Literal["weld:prepend", "smithed:prepend", "prepend"]


class InsertRule[SourceT: _Source](AdditiveRule[SourceT]):
    type: Literal["weld:insert", "smithed:insert", "insert"]
    index: int


class ReplaceRule[SourceT: _Source](AdditiveRule[SourceT]):
    type: Literal["weld:replace", "smithed:replace", "replace"]


class RemoveRule(BaseRule):
    type: Literal["weld:remove", "smithed:remove", "remove"]


# Generic parameterized rule union — SourceT flows through all additive variants.
# RemoveRule carries no source so it appears in every parameterization unchanged.
type RuleOf[SourceT: _Source] = Annotated[
    MergeRule[SourceT]
    | AppendRule[SourceT]
    | PrependRule[SourceT]
    | InsertRule[SourceT]
    | ReplaceRule[SourceT]
    | RemoveRule,
    Field(discriminator="type"),
    BeforeValidator(normalize_type),
]

# Concrete aliases for the two phases:
#   BroadRule  — parsed from raw JSON, source may still be a ReferenceSource
#   ResolvedRule — after resolution, all sources are guaranteed ValueSource
type BroadRule = RuleOf[BroadSource]
type ResolvedRule = RuleOf[ValueSource]

# Backward-compat alias — external code (e.g. handler.py) still imports `Rule`
type Rule = BroadRule
