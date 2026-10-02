from pydantic import BaseModel as _BaseModel

class BaseModel(_BaseModel): ...


# model_config = ConfigDict(json_encoders={dict: lambda v: list(v)})  # type: ignore
