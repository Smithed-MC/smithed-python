from contextlib import contextmanager
from importlib import resources
from typing import Iterable, Literal
from zipfile import ZipFile

from beet import Context, JsonFile, ProjectConfig, run_beet, subproject
from beet.core.utils import FileSystemPath, JsonDict
from jinja2 import Template

DESCRIPTION = "Merged by Smithed Weld"
FABRIC_MOD_TEMPLATE = Template(
    (resources.files("weld") / "fabric.mod.json.j2").read_text()
)


@contextmanager
def run_weld(
    packs: Iterable[str] | Iterable[ZipFile],
    config: FileSystemPath | ProjectConfig | JsonDict = {},
    directory: FileSystemPath | None = None,
    pack_types: list[Literal["data_pack", "resource_pack"]] = ["data_pack"],
):
    if type(config) is dict:
        config |= {
            "output": "dist",
        }
        for pack_type in pack_types:
            config[pack_type] = {
                "zipped": True,
                "description": DESCRIPTION,
                "name": "welded-pack",
            },

    with run_beet(config, directory=directory) as ctx:
        # ctx.require("weld.setup")
        for pack in packs:
            for pack_type in pack_types:
                match pack:
                    case str(name):
                        ctx.require(
                            subproject(
                                {
                                    pack_type: {"load": name},
                                    "pipeline": ["weld.print_pack_name"],
                                }
                            )
                        )
                    case ZipFile() as file:
                        if pack_type == "data_pack":
                            ctx.data.load(file)
                        else:
                            ctx.assets.load(file)

        yield ctx


def output_fabric_mod(ctx: Context):
    with ctx.override():
        ctx.data.extra["fabric.mod.json"] = JsonFile(FABRIC_MOD_TEMPLATE.render(
            packs=
        ))
        


def print_pack_name(ctx: Context):
    """Prints the merging pack name"""

    if not ctx.data and not ctx.assets:
        return

    print(
        f"Merging {'data' if ctx.data else 'resource'} pack:"
        f" {ctx.data.name or ctx.assets.name or 'Unknown'}"
    )
