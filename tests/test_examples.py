import logging
import os
from pathlib import Path

from beet.library.test_utils import ignore_name
import pytest
from lectern import Document
from lectern.pytest_plugin import FmtPackMarkdown
from pytest_insta import SnapshotFixture


from smithed.type import JsonDict
from smithed.weld import run_weld, scripts


class FmtWeldPackMarkdown(FmtPackMarkdown):
    def dump(self, path: Path, value: Document):
        if any(
            pack[scripts.WeldScript]
            for pack in (value.assets, *value.assets.overlays.values())
        ):
            # Lectern's shared @weld_script directive always loads into data.
            value.directives.add_resolver(
                lambda registry: registry.pop("weld_script", None)
            )
        super().dump(path, value)

    def load(self, path: Path) -> Document:
        document = Document()
        scripts.load_resources(document.assets)
        scripts.load_resources(document.data)

        pack_directives = {
            name: document.directives[name] for name in ("data_pack", "resource_pack")
        }

        def load_pack_fragment(fragment, assets, data):
            scripts.load_resources(assets)
            scripts.load_resources(data)
            pack_directives[fragment.directive](fragment, assets, data)

        for name in pack_directives:
            document.directives[name] = load_pack_fragment

        document.load(path)
        for pack in (document.assets, document.data):
            ignore_name(pack)
            for overlay in pack.overlays.values():
                ignore_name(overlay)
        return document


EXAMPLES = [f for f in os.listdir("examples") if not f.startswith(".")]

# Keep vanilla contents stable when beet updates its default Minecraft version.
TEST_CONFIG: JsonDict = {"minecraft": "1.21.11"}

OVERLAY_EXPECTATIONS = {
    "basic_overlays": [
        (60, ["first", "second"]),
        (61, ["first_overlay", "second_overlay"]),
        (62, ["first", "second"]),
    ],
    "complex_overlays": [
        (47, ["data", "second"]),
        (48, ["overlay_48_61", "second"]),
        (50, ["overlay_48_61", "second"]),
        (51, ["overlay_51_64", "second"]),
        (61, ["overlay_51_64", "second"]),
        (62, ["overlay_62_inf", "second"]),
        (65, ["overlay_62_inf", "second"]),
        (2**31 - 1, ["overlay_62_inf", "second"]),
    ],
}


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.parametrize("directory", EXAMPLES)
def test_build(
    snapshot: SnapshotFixture, directory: str, caplog: pytest.LogCaptureFixture
):
    packs = sorted(
        [
            f"examples/{directory}/{pack.name}"
            for pack in (Path("examples") / directory).glob("*")
            if pack.is_dir() or pack.suffix == ".md"
        ]
    )
    with (
        caplog.at_level(logging.DEBUG, logger="weld"),
        run_weld(packs, config=TEST_CONFIG) as ctx,
    ):
        # Check effective files independently of baking and snapshot acceptance.
        # A snapshot update must not hide a wrong format boundary or contribution.
        for pack_format, names in OVERLAY_EXPECTATIONS.get(directory, []):
            table = ctx.data.loot_tables["minecraft:entities/wither"]
            for entry in ctx.data.mcmeta.data.get("overlays", {}).get("entries", []):
                lower, upper = entry["formats"]
                if lower <= pack_format <= upper:
                    table = ctx.data.overlays[entry["directory"]].loot_tables.get(
                        "minecraft:entities/wither", table
                    )
            assert [
                item["name"] for pool in table.data["pools"] for item in pool["entries"]
            ] == [f"minecraft:{name}" for name in names]

        actual = ctx.inject(Document)
        actual.markdown_serializer.flat = True

        # assert no errors
        for record in caplog.records:
            match record.levelname:
                case "ERROR":
                    raise AssertionError("Logger revealed error")
                # case "WARNING":
                #     raise AssertionError("Logger revealed warning")
                case _:
                    ...

        # ignore pack format
        expected = snapshot("pack.md")
        if hasattr(expected, "assets"):
            expected.assets.pack_format = actual.assets.pack_format
            expected.assets.min_format = actual.assets.min_format
            expected.assets.max_format = actual.assets.max_format
            for overlay in expected.assets.overlays.values():
                del overlay.mcmeta
        if hasattr(expected, "data"):
            expected.data.pack_format = actual.data.pack_format
            expected.data.min_format = actual.data.min_format
            expected.data.max_format = actual.data.max_format
            for overlay in expected.data.overlays.values():
                del overlay.mcmeta

        # Ignore names and synthetic overlay-local metadata on both sides.
        # The actual range metadata in the root pack.mcmeta remains compared.
        for overlay in actual.data.overlays.values():
            ignore_name(overlay)
            del overlay.mcmeta

        for overlay in actual.assets.overlays.values():
            ignore_name(overlay)
            del overlay.mcmeta

        assert expected == actual


def test_script_reads_do_not_replace_generated_resources(
    snapshot: SnapshotFixture, tmp_path: Path, caplog: pytest.LogCaptureFixture
):
    pack = tmp_path / "pack"
    files = {
        "pack.mcmeta": """{
            "id": "sandbox",
            "pack": {"min_format": [101, 0], "max_format": [101, 0]}
        }""",
        "data/sandbox/function/input.mcfunction": "say Original input\n",
        "data/sandbox/function/untouched.mcfunction": "say Untouched input\n",
        "data/sandbox/loot_table/input.json": '{"pools": []}',
        "data/sandbox/weld/script/main.bolt": """
for name, source in ctx.data.functions.items():
    lines = list(source.lines)
    text = source.text
table = ctx.data.loot_tables["sandbox:input"].data

function sandbox:input:
    say Regenerated after reading

loot_table sandbox:input {"type": "minecraft:generic", "pools": []}
""",
    }
    for relative, content in files.items():
        path = pack / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    with (
        caplog.at_level(logging.ERROR, logger="weld"),
        run_weld([str(pack)], config=TEST_CONFIG) as ctx,
    ):
        assert not caplog.records
        actual = ctx.inject(Document)
        actual.markdown_serializer.flat = True
        expected = snapshot("pack.md")
        for document in (actual, expected):
            if hasattr(document, "data"):
                for root in (document.assets, document.data):
                    ignore_name(root)
                    for overlay in root.overlays.values():
                        ignore_name(overlay)
                        del overlay.mcmeta

        assert expected == actual
