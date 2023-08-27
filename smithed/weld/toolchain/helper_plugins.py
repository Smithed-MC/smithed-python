from importlib import resources
from zipfile import ZipFile

from beet import Context, JsonFile
from jinja2 import Template

FABRIC_MOD_TEMPLATE = Template(
    (resources.files("weld") / "resources" / "fabric.mod.json.j2").read_text()
)


def print_pack_name(ctx: Context):
    """Prints the merging pack name"""

    if not ctx.data and not ctx.assets:
        return

    print(
        f"Merging {'data' if ctx.data else 'resource'} pack:"
        f" {ctx.data.name or ctx.assets.name or 'Unknown'}"
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
