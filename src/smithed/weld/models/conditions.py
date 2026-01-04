from typing import Literal, Union

from .base import BaseModel

Condition = Union["ConditionPackCheck", "ConditionInverted"]


class ConditionPackCheck(BaseModel):
    type: Literal["pack_check", "weld:pack_check", "smithed:pack_check"]
    id: str


class ConditionInverted(BaseModel):
    type: Literal["inverted", "weld:inverted", "smithed:inverted"]
    conditions: list["Condition"]


ConditionInverted.update_forward_refs()
