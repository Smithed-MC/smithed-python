import logging
from pathlib import Path

import pytest

from smithed.weld import run_weld


@pytest.mark.parametrize(
    ("source", "error"),
    [
        ("import os", "Access forbidden module 'os'."),
        ("import collections.abc", "Access forbidden module 'collections.abc'."),
        ("from json import load", "Access forbidden attribute 'load'"),
        (
            "from typing import get_type_hints",
            "Access forbidden attribute 'get_type_hints'",
        ),
        ("from string import Formatter", "Access forbidden attribute 'Formatter'"),
        ('"test".__class__', "Access forbidden attribute '__class__'"),
        ("breakpoint()", 'Identifier "breakpoint" is not defined.'),
    ],
    ids=[
        "module",
        "submodule",
        "file_io",
        "annotation_eval",
        "formatter",
        "private_attribute",
        "debugger",
    ],
)
def test_sandbox_rejects_forbidden_access(
    tmp_path: Path, caplog: pytest.LogCaptureFixture, source: str, error: str
):
    pack = tmp_path / "pack"
    script = pack / "data/sandbox/weld/script/main.bolt"
    script.parent.mkdir(parents=True)
    script.write_text(
        f"{source}\n\nfunction sandbox:should_not_exist:\n    say Forbidden access succeeded\n"
    )
    (pack / "pack.mcmeta").write_text(
        '{"pack": {"pack_format": 101, "description": "Sandbox rejection"}}'
    )

    with (
        caplog.at_level(logging.ERROR, logger="weld"),
        run_weld([str(pack)], config={"minecraft": "1.21.11"}) as ctx,
    ):
        assert error in caplog.text
        assert all(
            "sandbox:should_not_exist" not in data.functions
            for data in (ctx.data, *ctx.data.overlays.values())
        )
