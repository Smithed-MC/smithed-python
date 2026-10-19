"""
Test the output via the python API for weld to ensure that empty data / resource packs
 aren't emitted when prompted for.
"""

import json
from zipfile import ZipFile

import pytest

from smithed.weld import run_weld


@pytest.mark.parametrize("order", [(101, 8), (8, 101)])
def test_output_preserves_newest_format_and_folders(tmp_path, order):
    newest_format = {
        "pack_format": 101,
        "min_format": [101, 1],
        "max_format": [9999, 0],
    }
    formats = {101: newest_format, 8: {"pack_format": 8, "supported_formats": [8, 8]}}
    packs = []
    for pack_format in order:
        source = tmp_path / f"pack_{pack_format}.zip"
        with ZipFile(source, "w") as archive:
            archive.writestr(
                "pack.mcmeta",
                json.dumps({"pack": {"description": "test", **formats[pack_format]}}),
            )
            archive.writestr(
                f"data/test/function/from_{pack_format}.mcfunction", "say test"
            )
            if pack_format == 101:
                archive.writestr(
                    "data/test/advancement/test.json",
                    '{"criteria": {"test": {"trigger": "minecraft:tick"}}}',
                )
        packs.append(str(source))

    output = tmp_path / "output.zip"
    with run_weld(packs, config={"minecraft": "1.21.11"}) as ctx:
        ctx.data.save(path=output, overwrite=True)

    with ZipFile(output) as archive:
        metadata = json.loads(archive.read("pack.mcmeta"))["pack"]
        assert metadata == {"description": "test", **newest_format}
        assert {name for name in archive.namelist() if name.startswith("data/")} == {
            "data/test/function/from_101.mcfunction",
            "data/test/function/from_8.mcfunction",
            "data/test/advancement/test.json",
        }
