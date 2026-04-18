import logging
import os
from pathlib import Path

from beet.library.test_utils import ignore_name
import pytest
from lectern import Document
from pytest_insta import SnapshotFixture


from smithed.type import JsonDict
from smithed.weld import run_weld

EXAMPLES = [f for f in os.listdir("examples") if not f.startswith(".")]

TEST_CONFIG: JsonDict = {}


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
        if hasattr(expected, "data"):
            expected.data.pack_format = actual.data.pack_format
            expected.data.min_format = actual.data.min_format
            expected.data.max_format = actual.data.max_format

        # ignore overlay names
        for overlay in actual.data.overlays.values():
            ignore_name(overlay)
            del overlay.mcmeta

        for overlay in actual.assets.overlays.values():
            ignore_name(overlay)
            del overlay.mcmeta

        assert expected == actual
