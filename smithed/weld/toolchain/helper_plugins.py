from importlib import resources
from zipfile import ZipFile

from beet import Context, JsonFile
from jinja2 import Template

from logging import Logger

logger = Logger(__name__)

FABRIC_MOD_TEMPLATE = Template(
    (resources.files("weld") / "resources" / "fabric.mod.json.j2").read_text()
)


def print_pack_name(ctx: Context):
    """Prints the merging pack name"""

    if not ctx.data and not ctx.assets:
        return

    logger.info(
        f"[dark_gray]Merging {'data' if ctx.data else 'resource'}pack:[/dark_gray]"
        f"[foreground] {ctx.data.name or ctx.assets.name or 'Unknown'}[/foreground]"
    )


def add_fabric_mod_json(ctx: Context, packs: list[str] | list[ZipFile]):
    ctx.data.extra["fabric.mod.json"] = JsonFile(
        FABRIC_MOD_TEMPLATE.render(
            packs=packs,
            pack_names=[
                pack.filename if type(pack) is ZipFile else pack for pack in packs
            ],
            mc_version=ctx.minecraft_version,
        )
    )
