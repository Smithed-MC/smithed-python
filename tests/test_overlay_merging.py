"""Focused behavioral regressions for overlay-aware welding."""

from copy import deepcopy

from beet import DataPack, Function, LootTable, Predicate
import pytest

from smithed.weld import run_weld
from smithed.weld.merging.handler import ConflictsHandler
from smithed.weld.toolchain.process import PackProcessor, PackWithName


def _weld_sources(monkeypatch, sources):
    monkeypatch.setattr(
        PackProcessor,
        "create_packs",
        lambda self, name: [PackWithName(sources[name], name)],
    )
    return run_weld(sources, config={"minecraft": "1.21.11"})


def _file_at_format(pack, file_type, path, pack_format):
    """Select a physical file directly, independently of Weld's baking helper."""
    result = pack[file_type].get(path)
    for overlay in pack.overlays.values():
        lower, upper = overlay.supported_formats
        if lower <= pack_format <= upper and path in overlay[file_type]:
            result = overlay[file_type][path]
    return result


def _reference_append(value):
    return LootTable(
        {
            "pools": [{"name": value}],
            "__smithed__": {
                "rules": [
                    {
                        "type": "smithed:append",
                        "target": "pools",
                        "source": {
                            "type": "smithed:reference",
                            "path": "pools[0]",
                        },
                    }
                ]
            },
        }
    )


def test_segments_resolve_original_references_and_apply_rules_once(monkeypatch):
    path = "minecraft:test"
    first, second = DataPack(), DataPack()
    first[LootTable][path] = _reference_append("first")
    second[LootTable][path] = _reference_append("second")
    first.overlays.setdefault("ten", supported_formats=[10, 10])[LootTable][path] = (
        _reference_append("ten")
    )
    first.overlays.setdefault("eleven", supported_formats=[11, 11])[LootTable][path] = (
        _reference_append("eleven")
    )
    originals = [first.copy(), second.copy()]
    vanilla = {"pools": []}
    monkeypatch.setattr(
        ConflictsHandler, "grab_vanilla", lambda self, path, kind: vanilla
    )

    with _weld_sources(monkeypatch, {"first": first, "second": second}) as ctx:
        for pack_format, expected in [
            (9, ["first", "second"]),
            (10, ["ten", "second"]),
            (11, ["eleven", "second"]),
            (12, ["first", "second"]),
        ]:
            actual = _file_at_format(ctx.data, LootTable, path, pack_format)
            assert [pool["name"] for pool in actual.data["pools"]] == expected

        assert [pack.name for pack in ctx.inject(PackProcessor).packs] == [
            "first",
            "second",
        ]
        assert all(name.startswith("smithed_generated_") for name in ctx.data.overlays)
        resolved = deepcopy(ctx.data[LootTable][path].data)
        ctx.inject(ConflictsHandler).process()
        assert ctx.data[LootTable][path].data == resolved

    assert first == originals[0]
    assert second == originals[1]
    assert vanilla == {"pools": []}


def test_all_matching_overlays_replace_each_physical_file_in_order(monkeypatch):
    source = DataPack()
    source[LootTable]["test:shared"] = LootTable({"marker": "base"})
    source[Function]["test:shared"] = Function(["say base"])
    source[Predicate]["test:early"] = Predicate({"marker": "base"})
    early = source.overlays.setdefault("early", supported_formats=[10, 11])
    early[LootTable]["test:shared"] = LootTable({"marker": "early"})
    early[Predicate]["test:early"] = Predicate({"marker": "early"})
    late = source.overlays.setdefault("late", supported_formats=[11, 12])
    late[LootTable]["test:shared"] = LootTable({"marker": "late"})
    late[Function]["test:shared"] = Function(["say late"])
    original = source.copy()

    with _weld_sources(monkeypatch, {"source": source}) as ctx:
        for pack_format, loot, predicate, function in [
            (9, "base", "base", "base"),
            (10, "early", "early", "base"),
            (11, "late", "early", "late"),
            (12, "late", "base", "late"),
            (13, "base", "base", "base"),
        ]:
            assert _file_at_format(
                ctx.data, LootTable, "test:shared", pack_format
            ).data == {"marker": loot}
            assert _file_at_format(
                ctx.data, Predicate, "test:early", pack_format
            ).data == {"marker": predicate}
            assert _file_at_format(
                ctx.data, Function, "test:shared", pack_format
            ).lines == [f"say {function}"]

    assert source == original


def test_equal_resolved_segment_does_not_emit_an_overlay(monkeypatch):
    first, second = DataPack(), DataPack()
    first[LootTable]["minecraft:test"] = _reference_append("first")
    second[LootTable]["minecraft:test"] = _reference_append("second")
    first.overlays.setdefault("same", supported_formats=[10, 10])[LootTable][
        "minecraft:test"
    ] = _reference_append("first")
    monkeypatch.setattr(
        ConflictsHandler, "grab_vanilla", lambda self, path, kind: {"pools": []}
    )

    with _weld_sources(monkeypatch, {"first": first, "second": second}) as ctx:
        assert not ctx.data.overlays
        assert [
            pool["name"] for pool in ctx.data[LootTable]["minecraft:test"].data["pools"]
        ] == [
            "first",
            "second",
        ]


@pytest.mark.parametrize("override_first", [True, False])
def test_override_skips_queued_rules_only_for_its_physical_file(
    monkeypatch, override_first
):
    path = "minecraft:test"
    override, second, third = DataPack(), DataPack(), DataPack()
    override[LootTable][path] = _reference_append("override")
    override[LootTable][path].data["__smithed__"]["override"] = True
    override[Predicate][path] = Predicate({"pools": []})
    for name, pack in [("second", second), ("third", third)]:
        pack[LootTable][path] = _reference_append(name)
        pack[Predicate][path] = Predicate(_reference_append(name).data)
    overlay = second.overlays.setdefault("ten", supported_formats=10)
    overlay[LootTable][path] = _reference_append("ten")
    overlay[Predicate][path] = Predicate(_reference_append("ten").data)
    inputs = [("second", second), ("third", third)]
    inputs.insert(0 if override_first else len(inputs), ("override", override))
    monkeypatch.setattr(
        ConflictsHandler, "grab_vanilla", lambda self, path, kind: {"pools": []}
    )

    with _weld_sources(monkeypatch, dict(inputs)) as ctx:
        for pack_format, expected in [(9, ["second", "third"]), (10, ["ten", "third"])]:
            loot = _file_at_format(ctx.data, LootTable, path, pack_format)
            predicate = _file_at_format(ctx.data, Predicate, path, pack_format)
            assert [pool["name"] for pool in loot.data["pools"]] == ["override"]
            assert [pool["name"] for pool in predicate.data["pools"]] == expected
