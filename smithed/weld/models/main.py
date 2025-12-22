import json
import logging
from typing import Any

from beet import ListOption
from pydantic import Field, model_validator

from ..merging.parser import get
from .base import BaseModel
from .priority import Priority
from .rules import AdditiveRule, Rule
from .sources import ReferenceSource, ValueSource

logger = logging.getLogger(__name__)


def deserialize(model: BaseModel, defaults: bool = True):
    """ Serialize a Pydantic model to dict.

    Uses Pydantic V2 API (model_dump_json) with fallback to V1 (json).
    """
    try:
        # Pydantic V2
        return json.loads(model.model_dump_json(
            by_alias=True, 
            exclude_defaults=not defaults
        ))
    except AttributeError:
        # Pydantic V1 fallback
        return json.loads(model.json(by_alias=True, exclude_defaults=not defaults))


def serialize_list_option(list_option: ListOption, defaults: bool = True) -> list:
    """ Serialize a ListOption to a list of dicts.

    Avoids the __root__ field issue by directly serializing the entries.
    """
    result = []
    for entry in list_option.entries():
        if isinstance(entry, BaseModel):
            result.append(deserialize(entry, defaults))
        else:
            # Already a dict
            result.append(entry)
    return result


class SmithedModel(BaseModel, extra="forbid"):
    id: str = ""
    version: int = 1
    override: bool | None = None  # only should be set by bundle packs
    priority: Priority | None = None
    rules: list[Rule] = []

    @model_validator(mode="before")
    def push_down_priorities(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Push down top-level priority to every rule.

        If a rule has a priority defined, it will not be overwritten.
        """

        rules: list[Rule] | None = values.get("rules")  # type: ignore
        priority: Priority | None = values.get("priority")  # type: ignore

        if rules is None:
            rules = []
            values["rules"] = rules

        if priority is None:
            priority = Priority()

        for rule in rules:
            if rule.priority is None:
                rule.priority = priority

        if "priority" in values:
            values.pop("priority")

        return values


class SmithedJsonFile(BaseModel, extra="allow"):
    """Accepts any standard JSON file from in-game, only needs as `__smithed__` field
    for custom merging logic"""

    smithed: ListOption[SmithedModel] = Field(
        default_factory=ListOption, alias="__smithed__"
    )

    @model_validator(mode="before")
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
