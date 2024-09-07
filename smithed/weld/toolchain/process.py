import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple
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
from beet.contrib.auto_yaml import use_auto_yaml
from beet.contrib.model_merging import model_merging
from beet.contrib.unknown_files import UnknownAsset, UnknownData

from ...type import JsonDict
from ..errors import InvalidMcmeta, InvalidPack

logger = logging.getLogger("weld")

_Pack = DataPack | ResourcePack


class PackWithName(NamedTuple):
    pack: _Pack
    name: str


@dataclass
class PackProcessor:
    ctx: Context
    file_id_cache: dict[JsonFileBase[JsonDict], _Pack] = field(default_factory=dict)
    packs: list[PackWithName] = field(default_factory=list)

    def __getitem__(self, key: JsonFileBase[JsonDict]):
        return self.file_id_cache[key]

    def __setitem__(self, key: JsonFileBase[JsonDict], value: _Pack):
        self.file_id_cache[key] = value

    def get_pack_type(self, path: ZipPath | Path) -> DataPack | ResourcePack:
        """TODO:"""
        if (path / "data").is_dir():
            pack = DataPack()
            pack.extend_namespace += [UnknownData]

        elif (path / "assets").is_dir():
            pack = ResourcePack()
            pack.extend_namespace += [UnknownAsset]
            model_merging(pack)

        else:
            raise InvalidPack(str(path))

        use_auto_yaml(pack)

        return pack

    def create_pack(self, file: str | ZipFile) -> DataPack | ResourcePack:
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

        def match_file(file: str | ZipFile) -> tuple[Path | ZipPath, str]:
            match file:
                case ZipFile() as f:
                    name = f.filename or "<unknown>"
                    if not name.endswith(".zip"):
                        name = f"{name}.zip"
                    return ZipPath(f), name

                case str() as name:
                    if name.endswith(".zip"):
                        return match_file(ZipFile(name))
                    return Path(name), name

        path, name = match_file(file)
        pack = self.get_pack_type(path)

        try:
            logger.info(f"Loading pack: {name}")
            pack.load(file)

        except DeserializationError as err:
            if isinstance(err.file, Mcmeta):
                raise InvalidMcmeta(pack=name, contents=err.file.get_content()) from err  # type: ignore
            raise err

        self.cache_pack(pack, name)

        return pack

    def load_pack(self, pack: DataPack | ResourcePack):
        """Loads a DataPack or ResourcePack into a context by merging it."""

        match pack:
            case DataPack() as dp:
                self.ctx.data.merge(dp)
            case ResourcePack() as rp:
                self.ctx.assets.merge(rp)

    def cache_pack(self, pack: DataPack | ResourcePack, name: str):
        """Cache some metadata from resource files to be used in later welding."""

        if "id" not in pack.mcmeta.data:
            pack.mcmeta.data["id"] = self.ctx.generate.format("missing_{incr}")

        for k in (
            PackQuery([pack]).distinct(match="*", extend=JsonFileBase[JsonDict]).keys()
        ):
            self[k] = pack

        self.packs.append(PackWithName(pack, name))

    def load_packs(self, packs: list[str] | list[ZipFile]):
        for pack in packs:
            self.load_pack(self.create_pack(pack))
