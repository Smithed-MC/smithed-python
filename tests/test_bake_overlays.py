from beet import DataPack, Function, FunctionTag
import pytest

from smithed.weld.toolchain.bake_overlays import bake_overlays_for_pack_format


def test_baking_applies_matching_overlays_per_file_in_declaration_order():
    pack = DataPack()
    pack.function_tags["test:shared"] = FunctionTag({"values": ["test:base"]})
    first = pack.overlays.setdefault("first", supported_formats=[10, 12])
    first.function_tags["test:shared"] = FunctionTag({"values": ["test:first"]})
    first.functions["test:earlier_only"] = Function("say earlier")
    last = pack.overlays.setdefault("last", supported_formats=11)
    last.function_tags["test:shared"] = FunctionTag({"values": ["test:last"]})
    inactive = pack.overlays.setdefault("inactive", supported_formats=[12, 13])
    inactive.functions["test:inactive"] = Function("say inactive")

    bake_overlays_for_pack_format(pack, 11)

    assert pack.function_tags["test:shared"].data == {"values": ["test:last"]}
    assert pack.functions["test:earlier_only"].text == "say earlier"
    assert "test:inactive" not in pack.functions
    assert not pack.overlays


def test_baked_tags_still_merge_between_packs_without_sharing_overlay_files():
    pack = DataPack()
    pack.function_tags["test:shared"] = FunctionTag({"values": ["test:base"]})
    overlay = pack.overlays.setdefault("overlay", supported_formats=11)
    overlay_tag = FunctionTag({"values": ["test:overlay"]})
    overlay.function_tags["test:shared"] = overlay_tag
    other = DataPack()
    other.function_tags["test:shared"] = FunctionTag({"values": ["test:other"]})

    bake_overlays_for_pack_format(pack, 11)
    pack.merge(other)

    assert pack.function_tags["test:shared"].data == {
        "values": ["test:overlay", "test:other"]
    }
    assert overlay_tag.data == {"values": ["test:overlay"]}


@pytest.mark.parametrize(
    "minimum,maximum,selected,expected",
    [
        ([82, 1], [82, 2], [82, 0], "say base"),
        ([82, 1], [82, 2], [82, 1], "say overlay"),
        ([82, 1], [82, 2], [82, 2], "say overlay"),
        ([82, 1], [82, 2], [82, 3], "say base"),
        (82, 82, [82, 100], "say overlay"),
        ([82], [82], [82, 100], "say overlay"),
    ],
)
def test_baking_honors_modern_bounds_even_with_legacy_formats(
    minimum, maximum, selected, expected
):
    pack = DataPack()
    pack.functions["test:shared"] = Function("say base")
    overlay = pack.overlays.setdefault(
        "modern",
        supported_formats=[10, 82],
        min_format=minimum,
        max_format=maximum,
    )
    overlay.functions["test:shared"] = Function("say overlay")

    bake_overlays_for_pack_format(pack, selected)

    assert pack.functions["test:shared"].text == expected
