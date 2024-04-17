import logging
from importlib import resources
from zipfile import ZipFile

from beet import Context, JsonFile, JsonFileBase
from jinja2 import Template

FABRIC_MOD_TEMPLATE = Template(
    (resources.files("smithed") / "weld/resources/fabric.mod.json.j2").read_text()
)

logger = logging.getLogger("weld")


def print_pack_name(ctx: Context):
    """Prints the merging pack name"""

    if not ctx.data and not ctx.assets:
        return

    logger.info(
        f"Loading {'data' if ctx.data else 'resource'}pack:"
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


def inject_pack_stuff_into_smithed(ctx: Context):
    """TODO: there needs to be a better way to inject the id, perhaps during proper
    preprocessing later in the process.
    """

    id = (
        ctx.data.mcmeta.data.get("id", ctx.generate.format("missing_{incr}"))
        if ctx.data
        else ctx.assets.mcmeta.data.get("id", ctx.generate.format("missing_{incr}"))
    )

    override = (
        ctx.data.mcmeta.data.get("__smithed__", {}).get("override", False)
        if ctx.data
        else ctx.assets.mcmeta.data.get("__smithed__", {}).get("override", False)
    )

    for namespace_file_type, data in ctx.query(match="*", extend=JsonFileBase).items():
        if not isinstance(data, dict):
            continue

        for namespace, resource in data.keys():
            if override:
                resource.data.setdefault("__smithed__", {})

            smithed = resource.data.get("__smithed__", False)
            if smithed is not False:
                if isinstance(smithed, list):
                    for item in smithed:  # type: ignore
                        item["id"] = id
                        if override:
                            smithed["override"] = override  # type: ignore
                elif isinstance(smithed, dict):
                    smithed["id"] = id
                    if override:
                        smithed["override"] = override
