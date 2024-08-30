from importlib import resources

from beet import Context, JsonFile
from jinja2 import Template

from smithed.weld import merging

FABRIC_MOD_TEMPLATE = Template(
    (resources.files("smithed") / "weld/resources/fabric.mod.json.j2").read_text()
)


def weld_handler(ctx: Context):
    ctx.require(merging.beet_default)


def weld(ctx: Context):
    ctx.require(merging.process)


def add_fabric_mod_json(ctx: Context, pack_names: list[str]):
    ctx.data.extra["fabric.mod.json"] = JsonFile(
        FABRIC_MOD_TEMPLATE.render(
            pack_hash=hash(pack_names),
            pack_names=pack_names,
            mc_version=ctx.minecraft_version,
        )
    )
