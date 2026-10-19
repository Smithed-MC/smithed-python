from beet import DataPack, ResourcePack
from beet.core.utils import SupportedFormats

type Pack = DataPack | ResourcePack
type PackFormat = tuple[int, int]
type FormatInput = int | list[int] | tuple[int, ...]
type FormatBounds = tuple[PackFormat, PackFormat]

MINOR_MAX = 2**31 - 1


def normalize_format(value: FormatInput, *, upper: bool = False) -> PackFormat:
    """Normalize Minecraft's integer or [major, minor] format notation.

    An integer upper bound includes every minor version of that major.
    https://www.minecraft.net/en-us/article/minecraft-snapshot-25w31a
    """
    match value:
        case int(major) | [int(major)] | (int(major),):
            minor = MINOR_MAX if upper else 0
        case [int(major), int(minor)] | (int(major), int(minor)):
            pass
        case _:
            raise ValueError(f"Unknown pack format structure {value}")
    if major < 0 or not 0 <= minor <= MINOR_MAX:
        raise ValueError(f"Invalid pack format {value}")
    return major, minor


def legacy_bounds(supported: SupportedFormats) -> FormatBounds:
    """Normalize a legacy formats range, which covers whole major versions."""
    match supported:
        case int(value):
            lower = upper = value
        case [int(lower), int(upper)]:
            pass
        case {"min_inclusive": int(lower), "max_inclusive": int(upper)}:
            pass
        case _:
            raise ValueError(f"Unknown supported formats structure {supported}")
    bounds = normalize_format(lower), normalize_format(upper, upper=True)
    if bounds[0] > bounds[1]:
        raise ValueError(f"Invalid supported formats range {supported}")
    return bounds


def get_overlay_bounds(overlay: Pack) -> FormatBounds | None:
    """Read authored modern bounds, falling back to a legacy formats range.

    Loaded packs must preserve the source metadata before beet adds defaults to
    overlay entries, so those defaults cannot mask legacy format constraints.
    """
    if overlay.min_format is not None or overlay.max_format is not None:
        if overlay.min_format is None or overlay.max_format is None:
            raise ValueError("An overlay must declare both min_format and max_format")
        bounds = (
            normalize_format(overlay.min_format),
            normalize_format(overlay.max_format, upper=True),
        )
        if bounds[0] > bounds[1]:
            raise ValueError(f"Invalid overlay format range {bounds}")
        return bounds
    if overlay.supported_formats is not None:
        return legacy_bounds(overlay.supported_formats)
    return None


def contains(bounds: FormatBounds, selected: FormatInput) -> bool:
    return bounds[0] <= normalize_format(selected) <= bounds[1]


def successor(value: PackFormat) -> PackFormat:
    major, minor = value
    return (major + 1, 0) if minor == MINOR_MAX else (major, minor + 1)


def predecessor(value: PackFormat) -> PackFormat:
    major, minor = value
    return (major - 1, MINOR_MAX) if minor == 0 else (major, minor - 1)


def legacy_overlay_threshold(pack: Pack) -> int:
    """First major format with minor-version support for this pack type."""
    return 82 if isinstance(pack, DataPack) else 65
