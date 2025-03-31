from dataclasses import dataclass, field
from copy import deepcopy
import itertools
import logging
import json
from pathlib import Path
from typing import Iterable, NamedTuple, cast
from zipfile import Path as ZipPath
from zipfile import ZipFile

from beet import (
    Context,
    DataPack,
    DeserializationError,
    JsonFileBase,
    Mcmeta,
    NamespaceFile,
    OverlayContainer,
    PackFile,
    PackQuery,
    ResourcePack,
    get_output_scope,
)

from beet.contrib.unknown_files import UnknownAsset, UnknownData
from beet.contrib.model_merging import model_merging
from beet.contrib.auto_yaml import use_auto_yaml
from beet.core.utils import SupportedFormats
from lectern import Document
import re

from .bake_overlays import bake_overlays_for_pack_format
from .formats import (
    FormatInput,
    MINOR_MAX,
    Pack,
    PackFormat,
    get_overlay_bounds,
    legacy_bounds,
    legacy_overlay_threshold,
    normalize_format,
    predecessor,
    successor,
)
from ..errors import InvalidMcmeta, InvalidPack
from smithed.weld import scripts
from ...type import JsonDict

logger = logging.getLogger("weld")

INFINITY_SENTINEL = 2**31 - 1
FILE_NAME_REGEX = re.compile(r"[^a-z\-_0-9]")


@dataclass(init=False)
class FormatRange:
    """Represents a pack format range [min, max]."""

    min: PackFormat
    max: PackFormat

    def __init__(self, min: FormatInput, max: FormatInput):
        self.min = normalize_format(min)
        self.max = normalize_format(max, upper=True)
        if self.min > self.max:
            raise ValueError(f"Invalid format range: {min} to {max}")

    def overlaps(self, other: "FormatRange") -> bool:
        """Check if this range overlaps with another range."""

        return not (self.max < other.min or self.min > other.max)

    def __hash__(self):
        return hash((self.min, self.max))

    def __eq__(self, other):
        if not isinstance(other, FormatRange):
            return False

        return self.min == other.min and self.max == other.max

    def __str__(self):
        """String representation for overlay name generation."""

        min_str = (
            str(self.min[0]) if self.min[1] == 0 else f"{self.min[0]}m{self.min[1]}"
        )
        max_str = (
            str(self.max[0])
            if self.max[1] == MINOR_MAX
            else f"{self.max[0]}m{self.max[1]}"
        )
        return f"{min_str}_{max_str}"


# Structure to track packs and their overlays by format range
@dataclass
class PackInfo[T: Pack]:
    base_pack: T
    overlays_by_range: dict[FormatRange, T]
    # Keeps overlays in declaration order for "last wins"
    overlays_in_order: list[tuple[FormatRange, T]]
    name: str


@dataclass
class SegmentResult[T: Pack]:
    """Stores the merged overlay content for a format segment."""

    segment: FormatRange
    overlay_pack: T  # The merged DataPack or ResourcePack for this segment


class PackWithName[T: Pack](NamedTuple):
    pack: T
    name: str

    @property
    def sanitized_name(self) -> str:
        """Get a sanitized version of the pack name suitable for file names."""
        name = (
            self.name.lower()
            .replace(" ", "_")
            .replace(".", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )
        return FILE_NAME_REGEX.sub("", name)


def as_range(supported_formats: SupportedFormats) -> FormatRange:
    """Converts SupportedFormats to FormatRange.

    Originally adapted from:
    https://github.com/Gamemode4Dev/GM4_Datapacks/blob/master/gm4/plugins/backwards.py#L168-L177
    """

    return FormatRange(*legacy_bounds(supported_formats))


def _create_empty_pack[T: (DataPack, ResourcePack)](pack_type: type[T]) -> T:
    """Create an empty DataPack or ResourcePack with default plugins configured.

    Default plugins:
    - UnknownData/UnknownAsset for handling unknown file types
    - use_auto_yaml for YAML support
    - model_merging for ResourcePacks (handles model conflict resolution)

    Args:
        pack_type: DataPack or ResourcePack class

    Returns:
        Configured empty pack
    """

    if pack_type is ResourcePack:
        pack = pack_type(extend_namespace=[UnknownAsset])
        use_auto_yaml(pack)
        model_merging(pack)
    elif pack_type is DataPack:
        pack = pack_type(extend_namespace=[UnknownData])
        use_auto_yaml(pack)
    else:
        raise ValueError("`pack_type` must be `DataPack` or `ResourcePack`")

    scripts.load_resources(pack)
    return pack


def _copy_pack[T: (DataPack, ResourcePack)](pack: T) -> T:
    """Copy files without replacing authored overlay bounds with beet defaults."""
    copied = pack.copy()
    if pack.overlay_parent is None:
        copied.mcmeta.data.pop("overlays", None)
        if "overlays" in pack.mcmeta.data:
            copied.mcmeta.data["overlays"] = deepcopy(pack.mcmeta.data["overlays"])
    return copied


def _has_namespaced_content(pack: Pack) -> bool:
    return any(pack.values()) or any(
        any(overlay.values()) for overlay in pack.overlays.values()
    )


def _file_content(file: PackFile | NamespaceFile) -> str | bytes:
    copied = file.copy()
    return (
        json.dumps(copied.data, sort_keys=True)
        if isinstance(copied, JsonFileBase)
        else copied.ensure_serialized()
    )


def _same_file(
    file: PackFile | NamespaceFile, other: PackFile | NamespaceFile | None
) -> bool:
    if other is None or type(file) is not type(other):
        return False
    # Python dict equality conflates JSON booleans, integers, and floats.
    if isinstance(file, JsonFileBase):
        return _file_content(file) == _file_content(other)
    return file == other


@dataclass
class PackProcessor:
    ctx: Context
    file_id_cache: dict[JsonFileBase[JsonDict], Pack] = field(default_factory=dict)
    packs: list[PackWithName[Pack]] = field(default_factory=list)

    def __post_init__(self):
        self.ctx.meta["packs"] = {}

    def __getitem__(self, key: JsonFileBase[JsonDict]):
        return self.file_id_cache[key]

    def __setitem__(self, key: JsonFileBase[JsonDict], value: Pack):
        self.file_id_cache[key] = value

    def create_packs(self, file: str | ZipFile) -> Iterable[PackWithName[Pack]]:
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
        packs: list[PackWithName[Pack]] = []

        try:
            logger.info(f"Loading pack: {name}")

            if isinstance(path, Path) and path.suffix in (".txt", ".md"):
                doc = Document(path=path)

                if _has_namespaced_content(doc.data):
                    packs.append(PackWithName(doc.data, name))

                if _has_namespaced_content(doc.assets):
                    packs.append(PackWithName(doc.assets, name))

            else:
                mcmeta_path = path / "pack.mcmeta"
                source_mcmeta = (
                    Mcmeta(mcmeta_path.read_text()).data
                    if mcmeta_path.is_file()
                    else {}
                )

                # Create empty packs with default plugins
                data = _create_empty_pack(DataPack)
                assets = _create_empty_pack(ResourcePack)

                # Load the files
                data.load(file)
                assets.load(file)

                # Beet creates overlays with the parent's default format bounds.
                # Restore authored entries so legacy ranges and undeclared
                # directories don't acquire synthetic modern bounds.
                for loaded in (data, assets):
                    loaded.mcmeta.data.pop("overlays", None)
                    if "overlays" in source_mcmeta:
                        loaded.mcmeta.data["overlays"] = deepcopy(
                            source_mcmeta["overlays"]
                        )
                    for overlay in loaded.overlays.values():
                        # Minecraft ignores these inside overlay directories.
                        # Keeping beet's synthetic mcmeta would reintroduce its
                        # defaults when the overlay is copied and rebound.
                        overlay.extra.pop("pack.mcmeta", None)
                        overlay.extra.pop("pack.png", None)

                # Only yield if there is actually content
                if _has_namespaced_content(data):
                    packs.append(PackWithName(data, name))

                if _has_namespaced_content(assets):
                    packs.append(PackWithName(assets, name))

        except DeserializationError as err:
            if isinstance(err.file, Mcmeta):
                cause = err.__cause__
                reason = str(cause)
                raise InvalidMcmeta(pack=name, cause=f"\n{reason}") from err
            raise err

        if packs:
            return packs

        raise InvalidPack(str(path))

    def load_pack[T: (DataPack, ResourcePack)](self, pack: PackWithName[T]) -> T:
        """Loads a DataPack or ResourcePack into a context by merging it.

        Keep an isolated source for provenance and segment baking, then merge a
        separate copy of its base content. Beet adopts incoming file objects, so
        merging the source itself would let conflict handling mutate later segments.

        Returns the isolated source, including its original overlays.
        """

        logger.debug(f"Loading pack '{pack.name}' base content")

        source = _copy_pack(pack.pack)
        self.cache_pack(PackWithName(source, pack.name))
        base = _copy_pack(source)
        base.overlays.clear()
        self.cache_pack(PackWithName(base, pack.name), register=False)

        match base:
            case DataPack() as dp:
                self.ctx.data.merge(dp)
            case ResourcePack() as rp:
                self.ctx.assets.merge(rp)

        return source

    def cache_pack[T: (DataPack, ResourcePack)](
        self, pack: PackWithName[T], *, register: bool = True
    ):
        """Cache some metadata from resource files to be used in later welding."""

        if "id" not in pack.pack.mcmeta.data:
            pack.pack.mcmeta.data["id"] = self.ctx.generate.format("missing_{incr}")

        for k in (
            PackQuery([pack.pack])
            .distinct(match="*", extend=JsonFileBase[JsonDict])
            .keys()
        ):
            self[k] = pack.pack

        if register:
            self.packs.append(pack)
            self.ctx.meta["packs"][pack.name] = pack.pack

    def load_packs(self, files: list[str] | list[ZipFile]):
        """Load a series of packs into `ctx`. Triggers merge policies.

        This method:
        1. Loads all base packs and merges them into ctx
        2. Collects all unique format ranges across all pack overlays (separately for data/resource)
        3. For each format range and pack type, generates a merged overlay by applying:
           - Base content from all packs (in order)
           - Overlay content from all packs that match this format (in order)
        """

        # Step 1: Load all base packs and index their overlays, separated by type
        data_pack_info, resource_pack_info = self._load_and_index_packs(files)

        # Keep each output's format metadata from its newest input pack.
        for pack_info, output in (
            (data_pack_info, self.ctx.data),
            (resource_pack_info, self.ctx.assets),
        ):
            if not pack_info:
                continue
            newest = max(
                (info.base_pack.mcmeta.data["pack"] for info in reversed(pack_info)),
                key=lambda metadata: normalize_format(
                    metadata.get("min_format", metadata.get("pack_format", 0))
                ),
            )
            for key in ("pack_format", "supported_formats", "min_format", "max_format"):
                output.mcmeta.data["pack"].pop(key, None)
                if key in newest:
                    output.mcmeta.data["pack"][key] = deepcopy(newest[key])

        # Remove pack-specific 'id' field from merged pack.mcmeta
        # The 'id' field is specific to individual packs and shouldn't appear in merged output
        # self.ctx.data.mcmeta.data.pop("id", None)
        # self.ctx.assets.mcmeta.data.pop("id", None)

        # Step 3: Generate merged overlays for each pack type separately
        if data_pack_info:
            self._generate_overlays_for_pack_type(data_pack_info, self.ctx.data)

        if resource_pack_info:
            self._generate_overlays_for_pack_type(resource_pack_info, self.ctx.assets)

        # remove id from all overlays
        for overlay in itertools.chain(
            self.ctx.data.overlays.values(), self.ctx.assets.overlays.values()
        ):
            overlay.mcmeta.data.pop("id", None)

    def _load_and_index_packs(
        self, files: list[str] | list[ZipFile]
    ) -> tuple[list[PackInfo[DataPack]], list[PackInfo[ResourcePack]]]:
        """Load all packs and index their overlays by format range.

        Returns:
            Tuple of (data_pack_info, resource_pack_info)
        """

        data_pack_info: list[PackInfo[DataPack]] = []
        resource_pack_info: list[PackInfo[ResourcePack]] = []

        def load_and_index[T: (DataPack, ResourcePack)](
            pack: T, name: str
        ) -> PackInfo[T]:
            source = self.load_pack(PackWithName(pack, name))
            overlays_by_range, overlays_in_order = self._index_overlays_by_range(
                PackWithName(source, name)
            )
            return PackInfo(source, overlays_by_range, overlays_in_order, name)

        for file in files:
            for pack in self.create_packs(file):
                # Separate by pack type
                if isinstance(pack.pack, DataPack):
                    data_pack_info.append(load_and_index(pack.pack, pack.name))
                else:
                    resource_pack_info.append(load_and_index(pack.pack, pack.name))

        return data_pack_info, resource_pack_info

    def _index_overlays_by_range[T: (DataPack, ResourcePack)](
        self, pack: PackWithName[T]
    ) -> tuple[dict[FormatRange, T], list[tuple[FormatRange, T]]]:
        """Index a pack's overlays by their format ranges.

        Args:
            pack: The pack to index

        Returns:
            Tuple of (overlays_by_range dict, overlays_in_order list)
            The list maintains declaration order for "last entry wins" logic.
        """

        overlays_by_range: dict[FormatRange, T] = {}
        overlays_in_order: list[tuple[FormatRange, T]] = []

        for overlay_name, raw_overlay in pack.pack.overlays.items():
            overlay = cast(T, raw_overlay)
            bounds = get_overlay_bounds(overlay)
            if bounds is None:
                logger.warning(
                    f"Overlay '{overlay_name}' in pack '{pack.name}' does not contain "
                    f"any supported formats. Ignoring."
                )
                continue

            format_range = FormatRange(*bounds)

            # Store the overlay reference - actual baking happens later during segment processing
            overlays_by_range[format_range] = overlay
            overlays_in_order.append((format_range, overlay))

        return overlays_by_range, overlays_in_order

    def _generate_overlays_for_pack_type[T: (DataPack, ResourcePack)](
        self, pack_info_list: list[PackInfo[T]], base_pack: T
    ):
        """Generate merged overlays using the 4-phase overlay-aware algorithm.

        Implements the algorithm from overlay_merging_report.md:
        Phase 1: Segment format space at all boundaries
        Phase 2: Use merged base pack (already in base_pack parameter)
        Phase 3: Compute effective states and diff against base
        Phase 4: Coalesce equal files across adjacent segments and assemble overlays

        Args:
            pack_info_list: List of PackInfo objects for this pack type
            base_pack: The base pack (ctx.data or ctx.assets) to store overlays in
        """

        from ..merging.handler import ConflictsHandler

        # We need to find the boundary of all of the overlay ranges so that we can find the
        #  most efficient segmentation for all of the overlays. Essentially, which overlays
        #  are related to which ranges so we can compute which final merged overlays we need.
        boundary_points = self._compute_boundary_points(pack_info_list)
        segments = self._generate_format_segments(boundary_points)
        if segments:
            self.ctx.inject(ConflictsHandler).process(base_pack)

        logger.info(
            f"Generated {len(segments)} format segments from {len(boundary_points)} boundary points"
        )

        # Once we have our segments, we can compute the effective state for each overlay segment.
        # Segments not produced are handled by the base pack (which requires no special behavior).
        segment_results: list[SegmentResult[T]] = []
        for segment in segments:
            overlay = self._create_overlay_for_segment(
                segment, pack_info_list, base_pack, type(base_pack)
            )
            if overlay is not None:
                segment_results.append(SegmentResult(segment, overlay))

        logger.info(f"Created {len(segment_results)} non-empty segment overlays")

        # Unrelated files can change at different boundaries. Join each file's
        # equal runs before grouping ranges, so those changes don't duplicate it.
        assembled = self._coalesce_segment_files(segment_results, type(base_pack))

        logger.info(f"Compacted to {len(assembled)} overlay ranges")

        # Minecraft versions using legacy metadata require formats on every entry,
        # including entries whose modern bounds cover newer versions only.
        threshold = legacy_overlay_threshold(base_pack)
        legacy_required = any(segment.min[0] < threshold for segment in assembled)
        overlays = cast(OverlayContainer[T], base_pack.overlays)

        for segment, overlay_pack in sorted(
            assembled.items(), key=lambda item: (item[0].min, item[0].max)
        ):
            overlay_name = f"smithed_generated_{segment}"
            # Each range needs its own object: binding an overlay changes its
            # parent/name, and later bounds must not overwrite an earlier entry.
            overlay = overlay_pack.copy()
            overlay.name = overlay_name
            overlay.min_format = segment.min
            overlay.max_format = (
                segment.max[0] if segment.max[1] == MINOR_MAX else segment.max
            )
            overlay.supported_formats = (
                [segment.min[0], segment.max[0]] if legacy_required else None
            )
            overlays[overlay_name] = overlay

        logger.info(f"Generated {len(base_pack.overlays)} final overlays")

    # ============================================================================
    # Phase 1: Format Space Segmentation
    # ============================================================================

    def _compute_boundary_points[T: (DataPack, ResourcePack)](
        self, pack_info_list: list[PackInfo[T]]
    ) -> list[PackFormat]:
        """Compute all format boundary points from overlays.

        Returns sorted list of boundary points where behavior might change.
        """

        points: set[PackFormat] = set()

        for pack_info in pack_info_list:
            for format_range, _ in pack_info.overlays_in_order:
                # Add the min boundary
                points.add(format_range.min)

                # Python integers can represent the exclusive endpoint even for
                # the sentinel. Omitting it would drop the final active segment.
                points.add(successor(format_range.max))

        return sorted(points)

    def _generate_format_segments(
        self, boundary_points: list[PackFormat]
    ) -> list[FormatRange]:
        """Generate non-overlapping format segments from boundary points.

        Returns list of FormatRange objects covering the entire format space.
        """

        if not boundary_points:
            return []

        segments = []

        # Create segments between consecutive boundary points
        for i in range(len(boundary_points) - 1):
            segments.append(
                FormatRange(boundary_points[i], predecessor(boundary_points[i + 1]))
            )

        return segments

    # ============================================================================
    # Phase 3: Effective State Merging
    # ============================================================================

    def _compute_merged_state_for_segment[T: (DataPack, ResourcePack)](
        self,
        segment: FormatRange,
        pack_info_list: list[PackInfo[T]],
        pack_type: type[T],
    ) -> T | None:
        """Compute the merged state for a segment across all packs.

        Apply each pack's matching overlays in declaration order before welding.
        Fresh copies keep rule resolution and execution isolated from other segments.
        """

        from ..merging.handler import ConflictsHandler
        from ..merging.plugin import apply_merging

        if not any(
            overlay_range.overlaps(segment)
            for pack_info in pack_info_list
            for overlay_range, _ in pack_info.overlays_in_order
        ):
            return None

        merged = _create_empty_pack(pack_type)
        merged.name = f"smithed_welded_{segment}"
        apply_merging(self.ctx.inject(ConflictsHandler), merged)

        for pack_info in pack_info_list:
            baked = _copy_pack(pack_info.base_pack)
            baked.name = pack_info.name
            bake_overlays_for_pack_format(baked, segment.min)
            self.cache_pack(PackWithName(baked, pack_info.name), register=False)
            merged.merge(baked)

        return merged

    def _create_overlay_for_segment[T: (DataPack, ResourcePack)](
        self,
        segment: FormatRange,
        pack_info_list: list[PackInfo[T]],
        base_pack: T,
        pack_type: type[T],
    ) -> T | None:
        """Create overlay for a segment, or None if no differences from base."""

        # Compute merged state for this segment
        merged_state = self._compute_merged_state_for_segment(
            segment, pack_info_list, pack_type
        )

        if merged_state is None:
            return None

        from ..merging.handler import ConflictsHandler

        self.ctx.inject(ConflictsHandler).process(merged_state)

        # Compare resolved outputs, not pending rules. Minecraft overlays replace
        # individual files, so an unchanged physical resource needs no overlay copy.
        for path, file in list(merged_state.all()):
            if _same_file(file, base_pack[type(file)].get(path)):
                del merged_state[type(file)][path]
        for namespace_name, namespace in merged_state.items():
            base_namespace = base_pack.get(namespace_name)
            for path, file in list(namespace.extra.items()):
                if base_namespace is not None and _same_file(
                    file, base_namespace.extra.get(path)
                ):
                    del namespace.extra[path]
        for path, file in list(merged_state.extra.items()):
            if path != "pack.mcmeta" and _same_file(file, base_pack.extra.get(path)):
                del merged_state.extra[path]

        if not merged_state:
            return None

        merged_state.name = f"smithed_generated_{segment}"

        return merged_state

    # ============================================================================
    # Phase 4: Deduplication & Assembly
    # ============================================================================

    def _coalesce_segment_files[T: (DataPack, ResourcePack)](
        self, segment_results: list[SegmentResult[T]], pack_type: type[T]
    ) -> dict[FormatRange, T]:
        """Join adjacent equal resolved files, then group files sharing a range.

        A missing/base-equal file breaks its run. Overlays may overlap, but each
        physical file has at most one active definition at any format.
        """
        type FileKey = tuple[
            str | None, type[NamespaceFile] | None, str, tuple[str, ...]
        ]
        versions: dict[FileKey, list[tuple[FormatRange, PackFile | NamespaceFile]]] = {}

        for result in sorted(segment_results, key=lambda item: item.segment.min):
            segment, pack = result.segment, result.overlay_pack
            # Match the metadata after beet attaches an overlay and drops its
            # local mcmeta. Range bounds can change a type's physical directory.
            layout = pack_type()
            layout.pack_format = None
            layout.max_format = (
                segment.max[0] if segment.max[1] == MINOR_MAX else segment.max
            )
            layout.supported_formats = [segment.min[0], segment.max[0]]
            for namespace_name, namespace in pack.items():
                for file_type, files in namespace.items():
                    scope = get_output_scope(file_type.scope, layout)
                    for path, file in files.items():
                        key = namespace_name, file_type, path, scope
                        versions.setdefault(key, []).append((segment, file))
                for path, file in namespace.extra.items():
                    key = namespace_name, None, path, ()
                    versions.setdefault(key, []).append((segment, file))
            for path, file in pack.extra.items():
                if path not in ("pack.mcmeta", "pack.png"):
                    versions.setdefault((None, None, path, ()), []).append(
                        (segment, file)
                    )

        assembled: dict[FormatRange, T] = {}
        for (namespace_name, file_type, path, _scope), entries in versions.items():
            runs: list[tuple[FormatRange, PackFile | NamespaceFile, str | bytes]] = []
            for segment, file in entries:
                content = _file_content(file)
                if runs:
                    previous, previous_file, previous_content = runs[-1]
                    if (
                        successor(previous.max) == segment.min
                        and type(previous_file) is type(file)
                        and previous_content == content
                    ):
                        runs[-1] = (
                            FormatRange(previous.min, segment.max),
                            previous_file,
                            previous_content,
                        )
                        continue
                runs.append((segment, file, content))

            for segment, file, _content in runs:
                if segment not in assembled:
                    assembled[segment] = _create_empty_pack(pack_type)
                target = assembled[segment]
                # These files are already welded. Assign copies directly so tags,
                # models, and Weld rules aren't merged or executed again.
                if namespace_name is None:
                    target.extra[path] = cast(PackFile, file.copy())
                elif file_type is None:
                    target[namespace_name].extra[path] = cast(PackFile, file.copy())
                else:
                    target[namespace_name][file_type][path] = cast(
                        NamespaceFile, file.copy()
                    )

        return assembled


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
