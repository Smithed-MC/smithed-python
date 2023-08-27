from typing import Literal

from .base import BaseModel


class ConditionPackCheck(BaseModel):
    type: Literal["pack_check", "smithed:pack_check"]
    id: str


class ConditionInverted(BaseModel):
    type: Literal["inverted", "smithed:inverted"]
    condition: "Condition"


Condition = ConditionPackCheck | ConditionInverted
