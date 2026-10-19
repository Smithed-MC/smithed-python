from typing import Any


def normalize_type(data: Any) -> Any:
    """Normalized the namespacing of types across discriminated unions.

    Leverage via `BeforeValidator`:

        Source = Annotated[
            ValueSource | ReferenceSource,
            BeforeValidator(normalize_source_type), # <--- Runs BEFORE the discriminator!
            Field(..., discriminator="type")
        ]
    """
    if isinstance(data, dict) and "type" in data:
        if isinstance(val := data["type"], str):
            if val.startswith("smithed:"):
                data["type"] = val.replace("smithed:", "weld:")
            elif ":" not in val:
                data["type"] = f"weld:{val}"

    return data
