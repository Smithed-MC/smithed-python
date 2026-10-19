import json
from pathlib import Path
import re

from beet import (
    BinaryFile,
    DataPack,
    Equipment,
    Function,
    Language,
    LootTable,
    Predicate,
    ResourcePack,
    run_beet,
)
import pytest

from smithed.weld.toolchain.plugins import weld_handler
from smithed.weld.toolchain.process import (
    INFINITY_SENTINEL,
    PackInfo,
    PackProcessor,
    PackWithName,
)


def weld_and_export(
    pack: DataPack | ResourcePack,
    output: Path,
    *,
    root_min_format: int | None = None,
) -> tuple[Path, list[dict]]:
    """Exercise segmentation, welding, deduplication, and beet's final export."""
    with run_beet({}, cache=False) as ctx:
        ctx.require(weld_handler)
        processor = ctx.inject(PackProcessor)
        source = processor.load_pack(PackWithName(pack, "ranges"))
        indexed, ordered = processor._index_overlays_by_range(
            PackWithName(source, "ranges")
        )
        target = ctx.data if isinstance(pack, DataPack) else ctx.assets
        if root_min_format is not None:
            target.min_format = root_min_format
            target.pack_format = root_min_format
            target.supported_formats = [root_min_format, target.max_format[0]]
        processor._generate_overlays_for_pack_type(
            [PackInfo(source, indexed, ordered, "ranges")], target
        )
        result = target.save(path=output)
    entries = json.loads((result / "pack.mcmeta").read_text())["overlays"]["entries"]
    return result, entries


def exported_overrides_at(
    output: Path, entries: list[dict], selected: tuple[int, int]
) -> dict[str, bytes]:
    """Read active exported files without using Weld's baking/range helpers."""
    files = {}
    for entry in entries:
        lower = tuple(entry["min_format"])
        upper = entry["max_format"]
        upper = (upper, 2**31 - 1) if isinstance(upper, int) else tuple(upper)
        if lower <= selected <= upper:
            directory = output / entry["directory"]
            for path in directory.rglob("*"):
                if path.is_file():
                    relative = path.relative_to(directory).as_posix()
                    assert relative not in files, f"Duplicate active file: {relative}"
                    files[relative] = path.read_bytes()
    return files


def test_equal_files_span_other_files_boundaries(tmp_path: Path):
    pack = DataPack()
    pack[Predicate]["test:changing"] = Predicate({"marker": None})
    stable = pack.overlays.setdefault("stable", min_format=[82, 1], max_format=[82, 6])
    stable[Predicate]["test:stable"] = Predicate({"marker": "stable"})
    stable["test"].extra["custom.bin"] = BinaryFile(b"namespace")
    stable.extra["custom-root.bin"] = BinaryFile(b"root")
    # Python considers 1, True, and 1.0 equal; their exported JSON types differ.
    for first, last, marker in [(1, 2, 1), (3, 4, True), (5, 6, 1.0)]:
        overlay = pack.overlays.setdefault(
            f"changing_{first}", min_format=[82, first], max_format=[82, last]
        )
        overlay[Predicate]["test:changing"] = Predicate({"marker": marker})

    output, entries = weld_and_export(pack, tmp_path / "output")

    assert [(entry["min_format"], entry["max_format"]) for entry in entries] == [
        ([82, 1], [82, 2]),
        ([82, 1], [82, 6]),
        ([82, 3], [82, 4]),
        ([82, 5], [82, 6]),
    ]
    assert len(list(output.glob("*/data/test/predicate/stable.json"))) == 1
    assert len(list(output.glob("*/data/test/custom.bin"))) == 1
    assert len(list(output.glob("*/custom-root.bin"))) == 1
    for minor, marker in [(1, 1), (2, 1), (3, True), (4, True), (5, 1.0), (6, 1.0)]:
        active = exported_overrides_at(output, entries, (82, minor))
        assert set(active) == {
            "data/test/predicate/changing.json",
            "data/test/predicate/stable.json",
            "data/test/custom.bin",
            "custom-root.bin",
        }
        changed = json.loads(active["data/test/predicate/changing.json"])["marker"]
        assert changed == marker
        assert type(changed) is type(marker)
        assert json.loads(active["data/test/predicate/stable.json"]) == {
            "marker": "stable"
        }
        assert active["data/test/custom.bin"] == b"namespace"
        assert active["custom-root.bin"] == b"root"
    assert not exported_overrides_at(output, entries, (82, 0))
    assert not exported_overrides_at(output, entries, (82, 7))


def test_json_type_changes_from_base_are_not_discarded(tmp_path: Path):
    pack = DataPack()
    pack[Predicate]["test:main"] = Predicate({"marker": 1})
    for minor, marker in [(1, True), (2, 1.0), (3, 1)]:
        overlay = pack.overlays.setdefault(
            f"minor_{minor}", min_format=[82, minor], max_format=[82, minor]
        )
        overlay[Predicate]["test:main"] = Predicate({"marker": marker})

    output, entries = weld_and_export(pack, tmp_path / "output")

    assert len(list(output.glob("*/data/test/predicate/main.json"))) == 2
    path = "data/test/predicate/main.json"
    for minor, marker in [(0, 1), (1, True), (2, 1.0), (3, 1), (4, 1)]:
        active = exported_overrides_at(output, entries, (82, minor))
        actual = json.loads(active.get(path, (output / path).read_bytes()))["marker"]
        assert actual == marker
        assert type(actual) is type(marker)
    assert not exported_overrides_at(output, entries, (82, 3))


def test_base_equal_and_inactive_gaps_break_file_runs(tmp_path: Path):
    pack = DataPack()
    for path in ("test:main", "test:other"):
        pack[Function][path] = Function("say base")
    broad = pack.overlays.setdefault("broad", min_format=[82, 1], max_format=[82, 3])
    broad[Function]["test:main"] = Function("say active")
    broad[Function]["test:other"] = Function("say other")
    restore = pack.overlays.setdefault(
        "restore", min_format=[82, 2], max_format=[82, 2]
    )
    restore[Function]["test:main"] = Function("say base")
    far = pack.overlays.setdefault("far", min_format=[82, 5], max_format=[82, 5])
    far[Function]["test:main"] = Function("say active")

    output, entries = weld_and_export(pack, tmp_path / "output")

    assert len(list(output.glob("*/data/test/function/other.mcfunction"))) == 1
    assert len(list(output.glob("*/data/test/function/main.mcfunction"))) == 3
    for minor, main, other in [
        (0, "base", "base"),
        (1, "active", "other"),
        (2, "base", "other"),
        (3, "active", "other"),
        (4, "base", "base"),
        (5, "active", "base"),
        (6, "base", "base"),
    ]:
        active = exported_overrides_at(output, entries, (82, minor))
        for name, marker in [("main", main), ("other", other)]:
            path = f"data/test/function/{name}.mcfunction"
            assert (
                active.get(path, (output / path).read_bytes())
                == f"say {marker}\n".encode()
            )


def test_disjoint_equal_content_keeps_each_exported_range(tmp_path: Path):
    pack = DataPack()
    pack[Function]["test:main"] = Function("say base")
    for version in (10, 11, 12):
        overlay = pack.overlays.setdefault(str(version), supported_formats=version)
        overlay[Function]["test:main"] = Function(
            "say different" if version == 11 else "say equal"
        )

    output, entries = weld_and_export(pack, tmp_path / "output")

    assert [entry["formats"] for entry in entries] == [[10, 10], [11, 11], [12, 12]]
    assert [entry["min_format"] for entry in entries] == [[10, 0], [11, 0], [12, 0]]
    assert [entry["max_format"] for entry in entries] == [10, 11, 12]
    assert [
        (output / entry["directory"] / "data/test/function/main.mcfunction").read_text()
        for entry in entries
    ] == ["say equal\n", "say different\n", "say equal\n"]


def test_terminal_sentinel_and_modern_minor_bounds_export(tmp_path: Path):
    pack = DataPack()
    pack[Function]["test:main"] = Function("say base")
    terminal = pack.overlays.setdefault(
        "terminal", supported_formats=[62, INFINITY_SENTINEL]
    )
    terminal[Function]["test:main"] = Function("say terminal")
    minor = pack.overlays.setdefault("minor", min_format=[82, 1], max_format=[82, 3])
    minor[Function]["test:main"] = Function("say minor")

    output, entries = weld_and_export(pack, tmp_path / "output")

    assert [(entry["min_format"], entry["max_format"]) for entry in entries] == [
        ([62, 0], [82, 0]),
        ([82, 1], [82, 3]),
        ([82, 4], INFINITY_SENTINEL),
    ]
    # One legacy range requires legacy formats on every entry.
    assert [entry["formats"] for entry in entries] == [
        [62, 82],
        [82, 82],
        [82, INFINITY_SENTINEL],
    ]
    assert [
        (output / entry["directory"] / "data/test/function/main.mcfunction").read_text()
        for entry in entries
    ] == ["say terminal\n", "say minor\n", "say terminal\n"]


def test_deduplication_preserves_resource_scope_and_extra_bytes(tmp_path: Path):
    pack = DataPack()
    pack[Function]["test:main"] = Function("say base")
    for version, file_type, payload in (
        (10, LootTable, b"first"),
        (11, Predicate, b"first"),
        (12, Predicate, b"second"),
    ):
        overlay = pack.overlays.setdefault(str(version), supported_formats=version)
        overlay[file_type]["test:shared"] = file_type({})
        overlay["test"].extra["custom.bin"] = BinaryFile(payload)
        overlay.extra["custom-root.bin"] = BinaryFile(payload)

    output, entries = weld_and_export(pack, tmp_path / "output")

    assert len(list(output.glob("*/data/test/predicate/shared.json"))) == 1
    assert len(list(output.glob("*/data/test/custom.bin"))) == 2
    assert len(list(output.glob("*/custom-root.bin"))) == 2
    for version, scope, payload in [
        (10, "loot_table", b"first"),
        (11, "predicate", b"first"),
        (12, "predicate", b"second"),
    ]:
        active = exported_overrides_at(output, entries, (version, 0))
        assert set(active) == {
            f"data/test/{scope}/shared.json",
            "data/test/custom.bin",
            "custom-root.bin",
        }
        assert json.loads(active[f"data/test/{scope}/shared.json"]) == {}
        assert active["data/test/custom.bin"] == payload
        assert active["custom-root.bin"] == payload


def test_equal_resources_keep_their_exported_physical_scopes(tmp_path: Path):
    pack = ResourcePack()
    pack[Equipment]["test:shared"] = Equipment({"marker": "base"})
    for name, lower, upper in [
        ("old", [45, 1], [45, 2]),
        ("new", [45, 3], [46, 1]),
    ]:
        overlay = pack.overlays.setdefault(name, min_format=lower, max_format=upper)
        overlay[Equipment]["test:shared"] = Equipment({"marker": "same"})

    output, entries = weld_and_export(pack, tmp_path / "output")

    # Beet picks the physical scope from final overlay metadata. Joining these
    # equal, adjacent resources would change the first range's exported path.
    for selected, scope in [
        ((45, 1), "models/equipment"),
        ((45, 2), "models/equipment"),
        ((45, 3), "equipment"),
        ((46, 1), "equipment"),
    ]:
        active = exported_overrides_at(output, entries, selected)
        assert set(active) == {f"assets/test/{scope}/shared.json"}
        assert json.loads(active[f"assets/test/{scope}/shared.json"]) == {
            "marker": "same"
        }


@pytest.mark.parametrize("pack_type,major", [(DataPack, 82), (ResourcePack, 65)])
def test_modern_only_output_uses_exact_bounds_without_legacy_formats(
    tmp_path: Path, pack_type: type[DataPack] | type[ResourcePack], major: int
):
    pack = pack_type()
    if isinstance(pack, DataPack):
        pack[Function]["test:main"] = Function("say base")
    else:
        pack[Language]["test:main"] = Language({"value": "base"})
    overlay = pack.overlays.setdefault(
        "minor", min_format=[major, 1], max_format=[major, 3]
    )
    if isinstance(pack, DataPack):
        overlay[Function]["test:main"] = Function("say minor")
    else:
        overlay[Language]["test:main"] = Language({"value": "minor"})

    # Legacy root support cannot permit formats when all overlay ranges are modern.
    output, entries = weld_and_export(pack, tmp_path / "output", root_min_format=60)

    assert len(entries) == 1
    assert entries[0]["min_format"] == [major, 1]
    assert entries[0]["max_format"] == [major, 3]
    assert "formats" not in entries[0]
    assert re.fullmatch(r"[a-z0-9_-]+", entries[0]["directory"])
    directory = output / entries[0]["directory"]
    if isinstance(pack, DataPack):
        assert (
            directory / "data/test/function/main.mcfunction"
        ).read_text() == "say minor\n"
    else:
        assert json.loads((directory / "assets/test/lang/main.json").read_text()) == {
            "value": "minor"
        }
