from collections import defaultdict
from itertools import chain
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, NamedTuple
from zipfile import Path as ZipPath
from zipfile import ZipFile

from beet import (
    Context,
    DataPack,
    DeserializationError,
    JsonFileBase,
    Mcmeta,
    PackQuery,
    ResourcePack,
)
from beet.contrib.unknown_files import UnknownAsset, UnknownData
from beet.contrib.model_merging import model_merging
from beet.contrib.auto_yaml import use_auto_yaml
from beet.core.utils import SupportedFormats
from lectern import Document

from ranges import Range, Inf, RangeDict

from ...type import JsonDict
from ..errors import InvalidMcmeta, InvalidPack

logger = logging.getLogger("weld")

_Pack = DataPack | ResourcePack


class PackWithName(NamedTuple):
    pack: _Pack
    name: str


def as_range(supported_formats: SupportedFormats | None) -> Range:
    """Checks whether a pack format is supported for a pack

    Originally adapted from:
    https://github.com/Gamemode4Dev/GM4_Datapacks/blob/master/gm4/plugins/backwards.py#L168-L177
    """

    match supported_formats:
        case int(value):
            return Range(value, value, include_end=True)
        case [min, max]:
            return Range(min, max, include_end=True)
        case {"min_inclusive": min, "max_inclusive": max}:
            return Range(min, max, include_end=True)
        case _:
            raise ValueError(f"Unexpected supported formats: {supported_formats}")


@dataclass
class PackProcessor:
    ctx: Context
    file_id_cache: dict[JsonFileBase[JsonDict], _Pack] = field(default_factory=dict)
    packs: list[PackWithName] = field(default_factory=list)

    def __getitem__(self, key: JsonFileBase[JsonDict]):
        return self.file_id_cache[key]

    def __setitem__(self, key: JsonFileBase[JsonDict], value: _Pack):
        self.file_id_cache[key] = value

    def create_packs(self, file: str | ZipFile) -> Iterable[PackWithName]:
        """Creates a DataPack or ResourcePack given a file (either ZipFile or str).

        1. Determine type of file and it's name to figure out how to load it.
        2. Peek inside to figure out if it's a data or resource pack.
        3. Create an empty pack and load some default plugin behavior:
        - `beet.contrib.unknown_files`
        - `beet.contrib.model_merging`
        - `beet.contrib.use_auto_yaml`
        4. Load the actual file into the empty pack object.
        5. Inject smithed specific information to some resource files within.
        6. Return the pack and it's name as a tuple.

        This process of loading the pack data in it's own object is isolated:
        - We need to load the pack data isolated so if there's an error within, we can
        surface it properly so it can be handled by the outer app. This allows us to
        skip the pack or just highlight the broken pack in a weld process.
        - File names, `pack.mcmeta`s, and the specific file tree gets lots when merged into
        a larger pack. While resource files themselves get conflict handled via our
        merger, the pack "metainfo" is useful enough for us to tabulate within itself.
        - Specific errors from invalid mcmeta and json files is useful to surface before the
        actual merging process.
        """

        path, name = get_pack_name(file)
        packs = []

        try:
            logger.info(f"Loading pack: {name}")

            if isinstance(path, Path) and path.suffix in (".txt", ".md"):
                doc = Document(path=path)

                if len(doc.data):
                    packs.append(PackWithName(doc.data, name))

                if len(doc.assets):
                    packs.append(PackWithName(doc.assets, name))

            else:
                # Empty packs that can handle unknown files
                data = DataPack(extend_namespace=[UnknownData])
                assets = ResourcePack(extend_namespace=[UnknownAsset])

                # default plugins
                use_auto_yaml(data)
                use_auto_yaml(assets)
                model_merging(assets)

                # load the files
                data.load(file)
                assets.load(file)

                # only yield if there is actually content
                if len(data):
                    packs.append(PackWithName(data, name))

                if len(assets):
                    packs.append(PackWithName(assets, name))

        except DeserializationError as err:
            if isinstance(err.file, Mcmeta):
                cause = err.__cause__
                reason = str(cause)
                raise InvalidMcmeta(pack=name, cause=f"\n{reason}") from err  # type: ignore
            raise err

        if packs:
            return packs

        raise InvalidPack(str(path))

    def load_pack(self, pack: DataPack | ResourcePack):
        """Loads a DataPack or ResourcePack into a context by merging it."""

        match pack:
            case DataPack() as dp:
                self.ctx.data.merge(dp)
            case ResourcePack() as rp:
                self.ctx.assets.merge(rp)

    def cache_pack(self, pack: PackWithName):
        """Cache some metadata from resource files to be used in later welding."""

        if "id" not in pack.pack.mcmeta.data:
            pack.pack.mcmeta.data["id"] = self.ctx.generate.format("missing_{incr}")

        for k in (
            PackQuery([pack.pack])
            .distinct(match="*", extend=JsonFileBase[JsonDict])
            .keys()
        ):
            self[k] = pack.pack

        self.packs.append(pack)

    def load_packs(self, files: list[str] | list[ZipFile]):
        """Load a series of packs into `ctx`. Triggers merge policies."""

        all_packs: list[_Pack] = []
        overlays: defaultdict[_Pack, RangeDict] = defaultdict(lambda: RangeDict(identity=True))  # type: ignore

        for file in files:
            # merge base packs
            for pack in (packs := self.create_packs(file)):
                overlay_for_pack = overlays[pack.pack]
                self.cache_pack(pack)
                self.load_pack(pack.pack)

                ## index overlays by their range
                # first, our base pack composes the entire range
                overlay_for_pack[Range(0, Inf)] = pack.pack

                # then, insert our overlays. this assumes we have no overlapping overlays
                for name, overlay in pack.pack.overlays.items():
                    if overlay.supported_formats is None:
                        logger.warning(
                            f"Overlay '{name}' does not contain any supported formats. Ignoring."
                        )
                        continue

                    # TODO: currently, if overlay ranges overlap, the behavior here is wrong.
                    overlay_for_pack[as_range(overlay.supported_formats)] = overlay

            all_packs += (pack.pack for pack in packs)

        # finally, we generate overlaps for every pack that we load.
        # for each packs' overlays, we check if they overlap with any other pack's overlays.
        # if there is an overlap, we merge against the overlapping pack/overlay into it's a new overlay.
        for pack in all_packs:
            for pack in chain([pack], pack.overlays.values()):
                for overlay_ranges in overlays.values():
                    overlaps: list[_Pack] = overlay_ranges.getoverlap(
                        as_range(pack.supported_formats)
                    )

                    generated_overlay = pack.__class__()
                    generated_overlay.merge(pack)  # type: ignore

                    for overlapping_pack in overlaps:
                        generated_overlay.merge(overlapping_pack)  # type: ignore


def get_pack_name(file: str | ZipFile) -> tuple[Path | ZipPath, str]:
    """Get pack path and name"""

    match file:
        case ZipFile() as f:
            name = f.filename or "<unknown>"
            if not name.endswith(".zip"):
                name = f"{name}.zip"
            return ZipPath(f), name

        case str() as name:
            if name.endswith(".zip"):
                return get_pack_name(ZipFile(name))
            return Path(name), name
