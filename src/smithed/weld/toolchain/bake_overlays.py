import logging
from dataclasses import replace
from typing import TypeVar

from beet.core.utils import SupportedFormats
from beet.library.data_pack import DataPack
from beet.library.resource_pack import ResourcePack
from beet.toolchain.context import PluginOptions

logger = logging.getLogger(__name__)

T = TypeVar("T", DataPack, ResourcePack)


class BakeOverlayOptions(PluginOptions):
    selected_data_format: int | None = None
    selected_assets_format: int | None = None


def bake_overlay(pack: T, overlay: T):
    """Bake an overlay onto an original pack."""

    original_policy = pack.merge_policy
    pack.merge_policy = replace(
        pack.merge_policy,
        namespace={namespace: [] for namespace in pack.get_file_types()},
    )

    pack.merge(overlay)

    pack.merge_policy = original_policy


def bake_overlays_for_pack_format(pack: T, pack_format: int):
    """Procedurally bake overlays conditionally based on a specific pack format that is supported.
    All overlays are then cleared from the original pack.
    """

    for name, overlay in pack.overlays.items():
        if overlay.supported_formats is None:
            continue

        if check_formats(overlay.supported_formats, pack_format):
            logger.info(f"Baking overlay '{name}'")
            bake_overlay(pack, overlay)

    pack.overlays.clear()


def check_formats(supported: SupportedFormats, pack_format: int) -> bool:
    """Checks whether a pack format is supported for a pack
    Originally adapted from:
    https://github.com/Gamemode4Dev/GM4_Datapacks/blob/master/gm4/plugins/backwards.py#L168-L177
    """

    match supported:
        case int(value):
            return value == pack_format
        case [min, max]:
            return min <= pack_format <= max
        case {"min_inclusive": min, "max_inclusive": max}:
            return min <= pack_format <= max
        case _:
            raise ValueError(f"Unknown supported formats structure {supported}")
