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


def inject_pack_id_into_smithed(ctx: Context):
    """CURSED"""

    id = (
        ctx.data.mcmeta.data.get("id", "missing")
        if ctx.data
        else ctx.assets.mcmeta.data.get("id", "missing")
    )

    for file in ctx.select(match="*", extend=JsonFileBase):
        try:
            if isinstance(file.data, list):  # type: ignore
                continue
            if smithed := file.data.get("__smithed__"):  # type: ignore
                if isinstance(smithed, list):
                    for item in smithed:
                        item["id"] = id
                elif isinstance(smithed, dict):
                    smithed["id"] = id
        except Exception:
            logger.warning(
                "Failed to inject pack id into smithed: %s", file.source_path
            )
