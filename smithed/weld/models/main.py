import logging
from typing import Any

from beet import ListOption
from jsonpath_ng import parse
from pydantic import Field, root_validator
from validators import validator

from .base import BaseModel
from .priority import Priority, PrioritySentinel
from .rules import AdditiveRule, Rule
from .sources import ReferenceSource, ValueSource

logger = logging.getLogger(__name__)


class SmithedModel(BaseModel, extra="forbid"):
    id: str = ""
    rules: list[Rule]
    priority: Priority = Priority()

    @validator("priority")
    def push_down_priorities(cls, value: Priority, values: dict[str, list[Rule]]):
        """Push down top-level priority to every rule.

        If a rule has a priority defined, it will not be overwritten.
        """

        for rule in values["rules"]:
            if rule.priority is PrioritySentinel:
                rule.priority = value


class SmithedJsonFile(BaseModel, extra="allow"):
    """Accepts any standard JSON file from in-game, only needs as `__smithed__` field
    for custom merging logic"""

    smithed: ListOption[SmithedModel] = Field(
        default_factory=ListOption, alias="__smithed__"
    )

    @root_validator
    def convert_type(cls, values: dict[str, ListOption[SmithedModel]]):
        for model in values["smithed"].entries():
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
                        rule.source = ValueSource(
                            value=parse(path).find(values).pop(0).value
                        )
                    except IndexError:
                        logger.warn(
                            f"Source Reference Path: {path} was not found, deleting."
                        )
                        continue
            yield rule
