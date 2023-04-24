import os

import pytest
from lectern import Document
from pytest_insta import SnapshotFixture
from weld import run_weld

EXAMPLES = [f for f in os.listdir("examples") if not f.startswith(".")]


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.parametrize("directory", EXAMPLES)
def test_build(snapshot: SnapshotFixture, directory: str):
    packs = (
        f"examples/{directory}/{pack}" for pack in os.listdir(f"examples/{directory}")
    )
    with run_weld(packs) as ctx:
        document = ctx.inject(Document)
        document.markdown_serializer.flat = True
        assert snapshot("pack.md") == document
