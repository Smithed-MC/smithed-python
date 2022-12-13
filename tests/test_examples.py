import os

import pytest
from beet import run_beet
from lectern import Document
from pytest_insta import SnapshotFixture

from weld.cli import run_weld


@pytest.mark.parametrize("directory", os.listdir("examples"))
def test_build(snapshot: SnapshotFixture, directory: str):
    with run_weld(directory=f"examples/{directory}") as ctx:
        document = ctx.inject(Document)
        document.markdown_serializer.flat = True
        assert snapshot("pack.md") == document
