"""Plugin for updating the Mecha command spec to the latest snapshot.

Source: https://github.com/TheWii/beet-plugins/blob/main/beet_plugins/latest_snapshot.py
"""

__all__ = [
    "beet_default",
    "latest_snapshot",
]


from beet import Context
from mecha import CommandTree, Mecha, delegate

COMMANDS_URL = (
    "https://raw.githubusercontent.com/misode/mcmeta/summary/commands/data.json"
)


def beet_default(ctx: Context):
    ctx.require(latest_snapshot)


def latest_snapshot(ctx: Context):
    """
    Fetches and updates the command tree of the Mecha command spec.
    This plugin should be placed before implicit execute, nested resources or bolt
    on the require list.
    """

    mc = ctx.inject(Mecha)

    path = ctx.cache["latest_commands"].download(COMMANDS_URL)
    mc.spec.add_commands(CommandTree.parse_file(path))

    mc.spec.parsers["command:argument:minecraft:gamemode"] = delegate("gamemode")
