import logging
import os
from pathlib import Path

import pytest
from lectern import Document
from pytest_insta import SnapshotFixture

from smithed.weld import run_weld

EXAMPLES = [f for f in os.listdir("examples") if not f.startswith(".")]

TEST_CONFIG = {
    "require": ["beet.contrib.auto_yaml"],
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
            if pack.is_dir()
        ]
    )
    with caplog.at_level(logging.WARNING), run_weld(packs, config=TEST_CONFIG) as ctx:
        document = ctx.inject(Document)
        document.markdown_serializer.flat = True

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
        snapshot_doc = snapshot("pack.md")
        snapshot_doc.assets.pack_format = document.assets.pack_format
        snapshot_doc.data.pack_format = document.data.pack_format

        assert snapshot_doc == document
