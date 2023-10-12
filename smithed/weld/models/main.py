import json
import logging
from typing import Any

from beet import ListOption
from pydantic import Field, root_validator, validator

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
    override: bool = False  # only should be set by bundle packs
    rules: list[Rule] = []
    priority: Priority | None = None

    @validator("priority", always=True)
    def push_down_priorities(cls, value: Priority, values: dict[str, list[Rule]]):
        """Push down top-level priority to every rule.

        If a rule has a priority defined, it will not be overwritten.
        """

        if value is None:
            return Priority()

        for rule in values["rules"]:
            if rule.priority is None:
                rule.priority = value


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
