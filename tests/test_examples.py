from pathlib import Path

import pytest
from lectern import Document
from pytest_insta import SnapshotFixture
from weld import run_weld


@pytest.mark.parametrize("directory", Path("examples").glob("*"))
def test_build(snapshot: SnapshotFixture, directory: Path):
    packs = (str(pack) for pack in directory.glob("*"))
    with run_weld(packs) as ctx:
        document = ctx.inject(Document)
        document.markdown_serializer.flat = True
        assert snapshot("pack.md") == document
