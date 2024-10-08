import json
import logging
from typing import Any

from beet import ListOption
from pydantic.v1 import Field, root_validator

from ..merging.parser import get
from .base import BaseModel
from .priority import Priority
from .rules import AdditiveRule, Rule
from .sources import ReferenceSource, ValueSource

logger = logging.getLogger(__name__)


def deserialize(model: BaseModel, defaults: bool = True):
    return json.loads(model.json(by_alias=True, exclude_defaults=not defaults))


class SmithedModel(BaseModel, extra="forbid"):
    id: str = ""
    version: int = 1
    override: bool | None = None  # only should be set by bundle packs
    priority: Priority | None = None
    rules: list[Rule] = []

    @root_validator
    def push_down_priorities(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Push down top-level priority to every rule.

        If a rule has a priority defined, it will not be overwritten.
        """

        rules: list[Rule] = values.get("rules")  # type: ignore
        priority: Priority | None = values.get("priority")  # type: ignore

        if priority is None:
            priority = Priority()

        for rule in rules:
            if rule.priority is None:
                rule.priority = priority

        values.pop("priority")

        return values


class SmithedJsonFile(BaseModel, extra="allow"):
    """Accepts any standard JSON file from in-game, only needs as `__smithed__` field
    for custom merging logic"""

    smithed: ListOption[SmithedModel] = Field(
        default_factory=ListOption, alias="__smithed__"
    )

    @root_validator
    def convert_type(cls, values: dict[str, ListOption[SmithedModel]]):
        if smithed := values.get("smithed"):
            for model in smithed.entries():
                model.rules = list(cls.convert_rules(model.rules, values))

        return values

    @classmethod
    def convert_rules(cls, rules: list["Rule"], values: dict[str, Any]):
        """Converts the source field of additive rules to a value source if it is
        a reference source, essentially "baking" it in for ease of use later.
        """

        for rule in rules:
            match isinstance(rule, AdditiveRule) and rule.source:
                case ReferenceSource(path=path):
                    try:
                        rule.source = ValueSource(value=get(values, path))
                    except ValueError:
                        logger.warn(
                            f"Source Reference Path: {path} was not found, deleting."
                        )
                        continue
            yield rule
