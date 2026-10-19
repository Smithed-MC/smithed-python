import logging

from beet.core.utils import SupportedFormats
from beet.toolchain.context import PluginOptions

from .formats import FormatInput, Pack, contains, get_overlay_bounds, legacy_bounds

logger = logging.getLogger(__name__)


class BakeOverlayOptions(PluginOptions):
    selected_data_format: FormatInput | None = None
    selected_assets_format: FormatInput | None = None


def bake_overlay[T: Pack](pack: T, overlay: T):
    """Replace files with copies from an overlay, preserving the pack's metadata.

    Overlay precedence applies to whole files, including tags and models whose
    normal merge behavior combines contents from separate packs.
    """

    for namespace_name, namespace in overlay.items():
        target = pack[namespace_name]
        for file_type, files in namespace.items():
            for path, file in files.items():
                target[file_type][path] = file.copy()
        for path, file in namespace.extra.items():
            target.extra[path] = file.copy()

    for path, file in overlay.extra.items():
        if path not in ("pack.mcmeta", "pack.png"):
            pack.extra[path] = file.copy()


def bake_overlays_for_pack_format(pack: Pack, pack_format: FormatInput):
    """Procedurally bake overlays conditionally based on a specific pack format that is supported.
    All overlays are then cleared from the original pack.
    """

    for name, overlay in pack.overlays.items():
        bounds = get_overlay_bounds(overlay)
        if bounds is None:
            continue

        if contains(bounds, pack_format):
            logger.info(f"Baking overlay '{name}'")
            bake_overlay(pack, overlay)

    pack.overlays.clear()


def check_formats(supported: SupportedFormats, pack_format: FormatInput) -> bool:
    """Checks whether a pack format is supported for a pack
    Originally adapted from:
    https://github.com/Gamemode4Dev/GM4_Datapacks/blob/master/gm4/plugins/backwards.py#L168-L177
    """

    return contains(legacy_bounds(supported), pack_format)
