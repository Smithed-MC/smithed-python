from typing import Annotated, Any, Iterable, Literal

from beet import ListOption
from jsonpath_ng import parse
from pydantic import BaseModel, Field, root_validator, validator


class ConditionPackCheck(BaseModel):
    type: Literal["smithed:pack_check"]
    id: str


class ConditionInverted(BaseModel):
    type: Literal["smithed:inverted"]
    condition: "SmithedCondition"


SmithedCondition = ConditionPackCheck | ConditionInverted


class SmithedReferenceSource(BaseModel):
    type: Literal["smithed:reference"]
    path: str


class SmithedValueSource(BaseModel):
    type: Literal["smithed:value"] = "smithed:value"
    value: Any


SmithedSource = SmithedReferenceSource | SmithedValueSource


class SmithedBaseRule(BaseModel):
    target: str
    source: SmithedSource = Field(..., discriminator="type")
    conditions: list[SmithedCondition] = []


class SmithedMergeRule(SmithedBaseRule):
    type: Literal["smithed:merge"]


class SmithedAppendRule(SmithedBaseRule):
    type: Literal["smithed:append"]


class SmithedPrependRule(SmithedBaseRule):
    type: Literal["smithed:prepend"]


class SmithedInsertRule(SmithedBaseRule):
    type: Literal["smithed:insert"]
    index: int


SmithedRule = Annotated[
    SmithedMergeRule | SmithedAppendRule | SmithedPrependRule | SmithedInsertRule,
    Field(..., discriminator="type"),
]


class SmithedPriority(BaseModel):
    after: set[str] = set()
    before: set[str] = set()

    @validator("*")
    def convert_fields(cls, value: Iterable[str]):
        return set(value)


class SmithedModel(BaseModel, extra="forbid"):
    id: str = ""
    rules: list[SmithedRule]
    priority: SmithedPriority = SmithedPriority()


class SmithedJsonFile(BaseModel, extra="allow"):
    smithed: ListOption[SmithedModel] = Field(
        default_factory=ListOption, alias="__smithed__"
    )

    @root_validator
    def convert_type(cls, values: dict[str, ListOption[SmithedModel]]):
        for model in values["smithed"].entries():
            for rule in model.rules:
                match rule.source:
                    case SmithedReferenceSource(path=path):
                        rule.source = SmithedValueSource(
                            value=parse(path).find(values).pop(0).value
                        )

        return values
