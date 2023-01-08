from contextlib import contextmanager
from typing import Iterable, Literal
from zipfile import ZipFile

from beet import Context, ProjectConfig, run_beet, subproject
from beet.core.utils import FileSystemPath, JsonDict

DESCRIPTION = "Merged by Smithed Weld"


@contextmanager
def run_weld(
    packs: Iterable[str] | Iterable[ZipFile],
    config: FileSystemPath | ProjectConfig | JsonDict = {},
    directory: FileSystemPath | None = None,
    pack_type: Literal["data_pack", "resource_pack"] = "data_pack",
):
    if type(config) is dict:
        config |= {
            "output": "dist",
            pack_type: {
                "zipped": True,
                "description": DESCRIPTION,
                "name": "merged-pack.zip",
            },
        }

    with run_beet(config, directory=directory) as ctx:
        # ctx.require("weld.setup")
        for pack in packs:
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


def print_pack_name(ctx: Context):
    """Prints the merging pack name"""

    if not ctx.data and not ctx.assets:
        return

    print(
        f"Merging {'data' if ctx.data else 'resource'} pack:"
        f" {ctx.data.name or ctx.assets.name or 'Unknown'}"
    )
