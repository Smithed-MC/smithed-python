"""Plugin for updating the Mecha command spec to the latest snapshot.

Source: https://github.com/TheWii/beet-plugins/blob/main/beet_plugins/latest_snapshot.py
"""

__all__ = [
    "beet_default",
    "latest_snapshot",
]


from typing import ClassVar

from beet import Context, JsonFile


class DamageType(JsonFile):
    """Class representing a damage type."""

    scope: ClassVar[tuple[str, ...]] = ("damage_type",)
    extension: ClassVar[str] = ".json"


def beet_default(ctx: Context):
    ctx.require(latest_snapshot)


def latest_snapshot(ctx: Context):
    """
    Fetches and updates the command tree of the Mecha command spec.
    This plugin should be placed before implicit execute, nested resources or bolt
    on the require list.
    """

    ctx.data.extend_namespace += [DamageType]
