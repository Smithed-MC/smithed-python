from typing import Annotated, Literal

from pydantic import BeforeValidator, Field

from .validators import normalize_type

from .base import BaseModel


class ConditionPackCheck(BaseModel):
    type: Literal["pack_check", "weld:pack_check", "smithed:pack_check"]
    id: str


class ConditionInverted(BaseModel):
    type: Literal["inverted", "weld:inverted", "smithed:inverted"]
    conditions: list["Condition"]


Condition = Annotated[
    ConditionPackCheck | ConditionInverted,
    BeforeValidator(normalize_type),
    Field(discriminator="type"),
]

# ConditionInverted.model_rebuild()
# ConditionPackCheck.model_rebuild()
