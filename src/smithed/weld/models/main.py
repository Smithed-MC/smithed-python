from dataclasses import field
import json
import logging
from typing import Any, Self

from attr import dataclass
from pydantic import model_validator, SerializeAsAny

from .base import BaseModel
from .priority import Priority
from .rules import Rule

logger = logging.getLogger(__name__)


def deserialize(model: BaseModel, defaults: bool = True):
    return json.loads(
        model.model_dump_json(
            by_alias=True, exclude_defaults=not defaults, exclude_none=True
        )
    )


class SmithedModel(BaseModel, extra="forbid"):
    id: str = ""
    version: int = 1
    override: bool | None = None  # only should be set by bundle packs
    priority: Priority | None = None
    rules: list[SerializeAsAny[Rule]] = []

    @model_validator(mode="after")
    def push_down_priorities(self) -> "SmithedModel":
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


@dataclass
class SmithedJsonFile:
    """Accepts any standard JSON file from in-game, only needs as `__smithed__` field
    for custom merging logic"""

    models: list[SmithedModel] = field(default_factory=list)

    @classmethod
    def process(cls, data: dict[str, Any]) -> Self | None:
        match data.get("__smithed__"):
            case list() as smithed_data:
                return cls(
                    models=[SmithedModel.model_validate(item) for item in smithed_data]
                )
            case dict() as smithed_data:
                return cls(models=[SmithedModel.model_validate(smithed_data)])
            case None:
                return
            case _:
                logger.warning(
                    f"Expected '__smithed__' field to be a list or dict, got {type(data['__smithed__']).__name__!r}"
                )
                return

    def conflict(self, other: Self) -> bool: ...
