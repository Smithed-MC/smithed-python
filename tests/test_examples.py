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
    def load(self, path: Path) -> Document:
        document = Document()
        scripts.load_resources(document.assets)
        scripts.load_resources(document.data)
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
