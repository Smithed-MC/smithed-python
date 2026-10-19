from dataclasses import field
import json
import logging
from typing import Self, cast

from attr import dataclass
from pydantic import model_validator, SerializeAsAny

from smithed.type import JsonDict, JsonList
from ..merging.parser import get

from .base import BaseModel
from .priority import Priority
from .rules import AdditiveRule, BroadRule, ResolvedRule, RuleOf
from .sources import _Source, BroadSource, ReferenceSource, ValueSource

logger = logging.getLogger(__name__)


def deserialize(model: BaseModel, defaults: bool = True):
    return json.loads(
        model.model_dump_json(
            by_alias=True, exclude_defaults=not defaults, exclude_none=True
        )
    )


class SmithedModel[SourceT: _Source](BaseModel, extra="forbid"):
    id: str = ""
    version: int = 1
    override: bool | None = None  # only should be set by bundle packs
    priority: Priority | None = None
    rules: list[SerializeAsAny[RuleOf[SourceT]]] = []

    @model_validator(mode="after")
    def push_down_priorities(self) -> "SmithedModel[SourceT]":
        """Push down top-level priority to every rule.

        If a rule has a priority defined, it will not be overwritten.
        """

        if self.priority is None:
            self.priority = Priority()

        for rule in self.rules:
            if rule.priority is None:
                rule.priority = self.priority

        self.priority = None

        return self


# Convenience aliases for the two lifecycle phases.
# These are proper Pydantic parameterized model classes and support .model_validate().
BroadSmithedModel = SmithedModel[BroadSource]
ResolvedSmithedModel = SmithedModel[ValueSource]


# ---------------------------------------------------------------------------
# Resolution helpers
# ---------------------------------------------------------------------------


def _resolve_source(source: BroadSource, raw: JsonDict) -> ValueSource:
    """Convert a BroadSource into a concrete ValueSource.

    For ValueSource this is a no-op. For ReferenceSource the path is looked up
    in `raw` via `get()` and the result is wrapped in a new ValueSource.
    Raises ValueError (from `get`) if the path does not exist in `raw`.
    """
    match source:
        case ValueSource():
            return source
        case ReferenceSource(path=path):
            return ValueSource(type="weld:value", value=get(raw, path))


def _resolve_rule(rule: BroadRule, raw: JsonDict) -> ResolvedRule | None:
    """Resolve the source of an additive rule.

    Returns None (and logs a warning) when the reference path cannot be found,
    the rule is dropped silently.
    """
    if isinstance(rule, AdditiveRule):
        try:
            resolved_source = _resolve_source(cast(BroadSource, rule.source), raw)  # type: ignore[arg-type]
        except ValueError:
            logger.warning(
                f"Source Reference Path: {rule.source.path!r} was not found, skipping rule."  # type: ignore[union-attr]
            )
            return None
        return rule.model_copy(update={"source": resolved_source})  # type: ignore[return-value]

    # RemoveRule has no source, so we return that directly
    return rule  # type: ignore[return-value]


def _resolve_model(model: BroadSmithedModel, raw: JsonDict) -> ResolvedSmithedModel:
    resolved_rules = [
        resolved
        for rule in model.rules
        if (resolved := _resolve_rule(rule, raw)) is not None
    ]
    return model.model_copy(update={"rules": resolved_rules})  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# File-level dataclasses
# ---------------------------------------------------------------------------


@dataclass
class SmithedJsonFile:
    """Accepts any standard JSON file from in-game, only needs a `__smithed__` field
    for custom merging logic. Sources remain broad (ValueSource | ReferenceSource)
    after `.process()`; call `.resolve()` to narrow them all to ValueSource."""

    data: JsonDict
    models: list[BroadSmithedModel] = field(default_factory=list)

    @classmethod
    def process(cls, data: JsonDict) -> Self:
        match data.get("__smithed__"):
            case list() as smithed_data:
                return cls(
                    data=data,
                    models=[
                        BroadSmithedModel.model_validate(item) for item in smithed_data
                    ],
                )
            case dict() as smithed_data:
                return cls(
                    data=data, models=[BroadSmithedModel.model_validate(smithed_data)]
                )
            case None:
                return cls(data=data, models=[])
            case _:
                logger.warning(
                    f"Expected '__smithed__' field to be a list or dict, got {type(data['__smithed__']).__name__!r}"
                )
                return cls(data=data, models=[])

    def resolve(self, raw: JsonDict | None = None) -> "ResolvedSmithedJsonFile":
        """Resolve all ReferenceSource instances into ValueSource.

        Args:
            raw: JSON data to resolve reference paths against.
                 Defaults to ``self.data`` when omitted.
        """
        context = raw if raw is not None else self.data
        return ResolvedSmithedJsonFile(
            data=self.data,
            models=[_resolve_model(model, context) for model in self.models],
        )

    def __bool__(self):
        return bool(self.models)

    def __eq__(self, other: object) -> bool:
        if type(other) is not type(self):
            raise ValueError(
                f"Cannot compare between {type(self)!r} and {type(other)!r}"
            )

        return self.data == self.data

    def dump_models(self) -> JsonList:
        return [deserialize(model, defaults=False) for model in self.models]


@dataclass
class ResolvedSmithedJsonFile:
    """Post-resolution form of SmithedJsonFile.

    All rule sources are guaranteed to be ValueSource — ReferenceSource
    cannot appear anywhere in this object's type tree."""

    data: JsonDict
    models: list[ResolvedSmithedModel]

    def __bool__(self):
        return bool(self.models)

    def dump_models(self) -> JsonList:
        return [deserialize(model, defaults=False) for model in self.models]
