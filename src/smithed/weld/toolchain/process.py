from dataclasses import dataclass, field
import hashlib
import itertools
import logging
import json
from pathlib import Path
from typing import Generic, Iterable, NamedTuple, TypeVar
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
import re

from .bake_overlays import bake_overlays_for_pack_format
from ..errors import InvalidMcmeta, InvalidPack
from ...type import JsonDict

logger = logging.getLogger("weld")

T = TypeVar("T", DataPack, ResourcePack)

INFINITY_SENTINEL = 2**31 - 1
FILE_NAME_REGEX = re.compile(r"[^a-z\-_0-9]")


@dataclass
class FormatRange:
    """Represents a pack format range [min, max]."""

    min: int
    max: int

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
            str(int(self.min))
            if self.min != float("inf") and self.min != float("-inf")
            else ""
        )
        max_str = (
            str(int(self.max))
            if self.max != float("inf") and self.max != float("-inf")
            else ""
        )
        return f"{min_str}_{max_str}"


# Structure to track packs and their overlays by format range
@dataclass
class PackInfo(Generic[T]):
    base_pack: T
    overlays_by_range: dict[FormatRange, T]
    # Keeps overlays in declaration order for "last wins"
    overlays_in_order: list[tuple[FormatRange, T]]
    name: str


@dataclass
class SegmentResult(Generic[T]):
    """Stores the merged overlay content for a format segment."""

    segment: FormatRange
    overlay_pack: T  # The merged DataPack or ResourcePack for this segment


class PackWithName(Generic[T], NamedTuple):
    pack: T
    name: str

    @property
    def sanitized_name(self) -> str:
        """Get a sanitized version of the pack name suitable for file names."""
        name = self.name.lower().replace(" ", "_").replace(".", "_")
        return FILE_NAME_REGEX.sub("", name)


def as_range(supported_formats: SupportedFormats) -> FormatRange:
    """Converts SupportedFormats to FormatRange.

    Originally adapted from:
    https://github.com/Gamemode4Dev/GM4_Datapacks/blob/master/gm4/plugins/backwards.py#L168-L177
    """

    match supported_formats:
        case int(value):
            return FormatRange(value, value)
        case [min, max]:
            return FormatRange(min, max)
        case {"min_inclusive": min, "max_inclusive": max}:
            return FormatRange(min, max)
        case _:
            raise ValueError(f"Unexpected supported formats: {supported_formats}")


def _create_empty_pack(pack_type: type[T]) -> T:
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
        model_merging(pack)  # type:  ignore
    elif pack_type is DataPack:
        pack = pack_type(extend_namespace=[UnknownData])
        use_auto_yaml(pack)
    else:
        raise ValueError("`pack_type` must be `DataPack` or `ResourcePack`")

    return pack


@dataclass
class PackProcessor(Generic[T]):
    ctx: Context
    file_id_cache: dict[JsonFileBase[JsonDict], T] = field(default_factory=dict)
    packs: list[PackWithName[T]] = field(default_factory=list)

    def __getitem__(self, key: JsonFileBase[JsonDict]):
        return self.file_id_cache[key]

    def __setitem__(self, key: JsonFileBase[JsonDict], value: T):
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
                # Create empty packs with default plugins
                data = _create_empty_pack(DataPack)
                assets = _create_empty_pack(ResourcePack)

                # Load the files
                data.load(file)
                assets.load(file)

                # Only yield if there is actually content
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

    def load_pack(self, pack: PackWithName[T]):
        """Loads a DataPack or ResourcePack into a context by merging it.

        NOTE: We only merge the BASE pack content, not overlays. Overlays will be
        processed separately in the overlay merging algorithm.

        Returns a copy of the pack without overlays that was used for merging.
        """

        logger.debug(f"Loading pack '{pack.name}' base content")

        # Transfer overlays to unique namespaced versions to avoid conflicts during merge
        for overlay_name, overlay in list(pack.pack.overlays.items()):
            name = f"{pack.sanitized_name}_{overlay_name}"
            overlay.name = name
            pack.pack.overlays[name] = overlay  # type: ignore
            del pack.pack.overlays[overlay_name]

        # Cache the pack without overlays so file lookups work during merge
        self.cache_pack(PackWithName(pack.pack, pack.name))

        match pack.pack:
            case DataPack() as dp:
                self.ctx.data.merge(dp)
            case ResourcePack() as rp:
                self.ctx.assets.merge(rp)

    def cache_pack(self, pack: PackWithName[T]):
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

        # Remove pack-specific 'id' field from merged pack.mcmeta
        # The 'id' field is specific to individual packs and shouldn't appear in merged output
        # self.ctx.data.mcmeta.data.pop("id", None)
        # self.ctx.assets.mcmeta.data.pop("id", None)

        # Step 3: Generate merged overlays for each pack type separately
        if data_pack_info:
            self._generate_overlays_for_pack_type(data_pack_info, self.ctx.data)  # type: ignore

        if resource_pack_info:
            self._generate_overlays_for_pack_type(resource_pack_info, self.ctx.assets)  # type: ignore

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

        data_pack_info: list[PackInfo] = []
        resource_pack_info: list[PackInfo] = []

        for file in files:
            for pack in self.create_packs(file):
                # Index overlays by their format ranges
                overlays_by_range, overlays_in_order = self._index_overlays_by_range(
                    pack
                )

                pack_info = PackInfo(
                    base_pack=pack.pack,
                    overlays_by_range=overlays_by_range,
                    overlays_in_order=overlays_in_order,
                    name=pack.name,
                )

                # Separate by pack type
                if isinstance(pack.pack, DataPack):
                    data_pack_info.append(pack_info)
                else:
                    resource_pack_info.append(pack_info)

                # Finally, load the pack
                self.load_pack(pack)

        return data_pack_info, resource_pack_info

    def _index_overlays_by_range(
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

        for overlay_name, overlay in pack.pack.overlays.items():
            if overlay.supported_formats is None:
                logger.warning(
                    f"Overlay '{overlay_name}' in pack '{pack.name}' does not contain "
                    f"any supported formats. Ignoring."
                )
                continue

            format_range = as_range(overlay.supported_formats)

            # Store the overlay reference - actual baking happens later during segment processing
            overlays_by_range[format_range] = overlay  # type: ignore
            overlays_in_order.append((format_range, overlay))  # type: ignore

        return overlays_by_range, overlays_in_order

    def _generate_overlays_for_pack_type(
        self, pack_info_list: list[PackInfo[T]], base_pack: T
    ):
        """Generate merged overlays using the 4-phase overlay-aware algorithm.

        Implements the algorithm from overlay_merging_report.md:
        Phase 1: Segment format space at all boundaries
        Phase 2: Use merged base pack (already in base_pack parameter)
        Phase 3: Compute effective states and diff against base
        Phase 4: Deduplicate and assemble final overlays

        Args:
            pack_info_list: List of PackInfo objects for this pack type
            base_pack: The base pack (ctx.data or ctx.assets) to store overlays in
        """

        # We need to find the boundary of all of the overlay ranges so that we can find the
        #  most efficient segmentation for all of the overlays. Essentially, which overlays
        #  are related to which ranges so we can compute which final merged overlays we need.
        boundary_points = self._compute_boundary_points(pack_info_list)
        segments = self._generate_format_segments(boundary_points)

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

        # After computing all of the segment overlays, we need to deduplicate them.
        # This ensures that we don't create multiple overlays with identical content.
        grouped = self._group_segments_by_content(segment_results)

        logger.info(f"Deduplicated to {len(grouped)} unique overlay groups")

        for _, (overlay_pack, segment_list) in grouped.items():
            # Merge adjacent/overlapping segments if possible
            merged_segments = self._merge_adjacent_segments(segment_list)

            # Create one overlay entry per merged segment range
            for merged_segment in merged_segments:
                overlay_name = f"smithed_generated_{merged_segment}"
                overlay_pack.name = overlay_name
                overlay_pack.supported_formats = [
                    merged_segment.min,
                    merged_segment.max,
                ]
                base_pack.overlays[overlay_name] = overlay_pack  # type: ignore

        logger.info(f"Generated {len(base_pack.overlays)} final overlays")

    # ============================================================================
    # Phase 1: Format Space Segmentation
    # ============================================================================

    def _compute_boundary_points(self, pack_info_list: list[PackInfo[T]]) -> list[int]:
        """Compute all format boundary points from overlays.

        Returns sorted list of boundary points where behavior might change.
        """

        points: set[int] = set()

        for pack_info in pack_info_list:
            for format_range, _ in pack_info.overlays_in_order:
                # Add the min boundary
                points.add(format_range.min)

                # Add max+1 boundary (unless it's the infinity sentinel)
                if format_range.max < INFINITY_SENTINEL:
                    points.add(format_range.max + 1)

        return sorted(points)

    def _generate_format_segments(
        self, boundary_points: list[int]
    ) -> list[FormatRange]:
        """Generate non-overlapping format segments from boundary points.

        Returns list of FormatRange objects covering the entire format space.
        """

        if not boundary_points:
            return []

        segments = []

        # Create segments between consecutive boundary points
        for i in range(len(boundary_points) - 1):
            segments.append(FormatRange(boundary_points[i], boundary_points[i + 1] - 1))

        return segments

    # ============================================================================
    # Phase 3: Effective State Merging
    # ============================================================================

    def _get_active_overlay(
        self, pack_info: PackInfo[T], segment: FormatRange
    ) -> T | None:
        """Find the last (winning) overlay that overlaps with the given segment.

        Implements "last entry wins" rule from Minecraft's overlay system.
        """
        # Iterate in reverse order (last overlay wins)
        for overlay_range, overlay_pack in reversed(pack_info.overlays_in_order):
            if overlay_range.overlaps(segment):
                return overlay_pack

        return None

    def _compute_merged_state_for_segment(
        self,
        segment: FormatRange,
        pack_info_list: list[PackInfo[T]],
        pack_type: type[T],
    ) -> T | None:
        """Compute the merged state for a segment across all packs.

        For each pack, computes effective state by merging overlay files with base files.
        Files present in the active overlay take precedence over base files.
        """

        from ..merging.handler import ConflictsHandler
        from ..merging.plugin import apply_merging

        # Create empty pack for merged result
        merged = _create_empty_pack(pack_type)
        merged.name = f"smithed_welded_{segment}"
        apply_merging(self.ctx.inject(ConflictsHandler), merged)
        active_paths = set()
        active_overlays = []

        # Gather the active paths
        for pack_info in pack_info_list:
            active_overlays.append(
                active_overlay := self._get_active_overlay(pack_info, segment)
            )

            if active_overlay is not None:
                active_paths |= set(path for (path, _) in active_overlay.all())

        # For each pack, merge its effective state for this segment
        for active_overlay, pack_info in zip(active_overlays, pack_info_list):
            # Check if any overlays are active for this segment
            active_overlay = self._get_active_overlay(pack_info, segment)

            if active_overlay is not None:
                # Bake the pack at this segment's format (this applies all overlays in order)
                baked = pack_info.base_pack.copy()
                baked.name = pack_info.name
                self.cache_pack(PackWithName(baked, baked.name))  # type: ignore
                # Use segment.min as the representative format for this range
                logger.debug(f"Baking pack '{pack_info.name}' for segment {segment}")
                bake_overlays_for_pack_format(baked, segment.min)

                for path, file_type in baked.all():
                    if path not in active_paths:
                        logger.debug(
                            f"Removing inactive file: {path} from baked overlay in pack '{baked.name}'"
                        )
                        baked[type(file_type)].pop(path)

                merged.merge(baked)  # type: ignore
            else:
                # No overlays active for this segment - use base pack as-is
                logger.debug(
                    f"No active overlay for pack '{pack_info.name}' in segment {segment}"
                )
                merged.merge(pack_info.base_pack)

        if len(merged) <= 0:
            return None

        return merged

    def _create_overlay_for_segment(
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

        if merged_state is not None:
            merged_state.name = f"smithed_generated_{segment}"
            merged_state.supported_formats = [segment.min, segment.max]

        return merged_state

    # ============================================================================
    # Phase 4: Deduplication & Assembly
    # ============================================================================

    def _compute_pack_hash(self, pack: T) -> str:
        """Compute a hash of pack contents for deduplication."""

        # Collect all files sorted by path for deterministic hashing
        content_parts = []
        for file_type in pack.get_file_types():
            namespace = pack[file_type]
            for path in sorted(namespace.keys()):
                file = namespace[path]
                # Serialize file data to JSON string (or use str for non-JSON files)
                if hasattr(file, "data"):
                    content_parts.append(
                        f"{path}:{json.dumps(file.data, sort_keys=True)}"  # type: ignore
                    )
                else:
                    content_parts.append(f"{path}:{str(file)}")

        # Hash the combined content
        content_str = "||".join(content_parts)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def _group_segments_by_content(
        self, segment_results: list[SegmentResult[T]]
    ) -> dict[str, tuple[T, list[FormatRange]]]:
        """Group segments with identical content.

        Returns: Dict mapping content hash to (overlay_pack, list of segments)
        """

        groups: dict[str, tuple[T, list[FormatRange]]] = {}

        for result in segment_results:
            content_hash = self._compute_pack_hash(result.overlay_pack)

            if content_hash in groups:
                # Add segment to existing group
                groups[content_hash][1].append(result.segment)
            else:
                # Create new group
                groups[content_hash] = (result.overlay_pack, [result.segment])

        return groups

    def _merge_adjacent_segments(
        self, segments: list[FormatRange]
    ) -> list[FormatRange]:
        """Merge adjacent or overlapping segments into continuous ranges."""
        if not segments:
            return []

        # Sort by min value
        sorted_segments = sorted(segments, key=lambda s: s.min)

        merged = [sorted_segments[0]]
        for segment in sorted_segments[1:]:
            last = merged[-1]

            # Check if adjacent or overlapping (adjacent means max + 1 == min)
            if last.max + 1 >= segment.min:
                # Merge by extending the last segment
                merged[-1] = FormatRange(last.min, max(last.max, segment.max))
            else:
                # Not adjacent, keep separate
                merged.append(segment)

        return merged


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
