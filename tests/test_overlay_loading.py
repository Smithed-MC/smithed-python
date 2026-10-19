import json
from zipfile import ZipFile

import pytest

from smithed.weld import run_weld


@pytest.mark.parametrize("zipped", [False, True])
def test_loading_preserves_authored_ranges_and_ignores_undeclared_overlays(
    tmp_path, zipped
):
    metadata = {
        "pack": {
            "description": "range regression",
            "pack_format": 60,
            "supported_formats": [60, 88],
            "min_format": 60,
            "max_format": 88,
        },
        "overlays": {
            "entries": [
                {"directory": "legacy", "formats": [60, 61]},
                {
                    "directory": "modern",
                    "formats": [88, 88],
                    "min_format": [88, 1],
                    "max_format": [88, 2],
                },
            ]
        },
    }
    files = {
        "pack.mcmeta": json.dumps(metadata),
        "data/test/function/shared.mcfunction": "say base",
        "legacy/data/test/function/shared.mcfunction": "say legacy",
        "modern/data/test/function/shared.mcfunction": "say modern",
        "undeclared/data/test/function/shared.mcfunction": "say undeclared",
    }
    if zipped:
        source = tmp_path / "pack.zip"
        with ZipFile(source, "w") as archive:
            for path, contents in files.items():
                archive.writestr(path, contents)
    else:
        source = tmp_path / "pack"
        for path, contents in files.items():
            target = source / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(contents)

    with run_weld([str(source)], config={"minecraft": "1.21.11"}) as ctx:
        assert len(ctx.data.overlays) == 2
        for selected, expected in [
            ((59, 0), "base"),
            ((60, 0), "legacy"),
            ((61, 0), "legacy"),
            ((62, 0), "base"),
            ((88, 0), "base"),
            ((88, 1), "modern"),
            ((88, 2), "modern"),
            ((88, 3), "base"),
        ]:
            actual = ctx.data.functions["test:shared"]
            for overlay in ctx.data.overlays.values():
                lower = tuple(overlay.min_format)
                upper = overlay.max_format
                upper = (upper, 2**31 - 1) if isinstance(upper, int) else tuple(upper)
                if lower <= selected <= upper:
                    actual = overlay.functions.get("test:shared", actual)
            assert actual.lines == [f"say {expected}"]


@pytest.mark.parametrize("kind", ["directory", "zip"])
def test_overlay_only_pack_loads_without_creating_empty_resource_pack(tmp_path, kind):
    metadata = {
        "pack": {"pack_format": 61, "description": "overlay only"},
        "overlays": {"entries": [{"directory": "only", "formats": [61, 62]}]},
    }
    if kind == "zip":
        source = tmp_path / "pack.zip"
        with ZipFile(source, "w") as archive:
            archive.writestr("pack.mcmeta", json.dumps(metadata))
            archive.writestr("only/data/test/function/main.mcfunction", "say overlay")
    else:
        source = tmp_path / "pack"
        contents = source / "only/data/test/function/main.mcfunction"
        contents.parent.mkdir(parents=True)
        contents.write_text("say overlay")
        (source / "pack.mcmeta").write_text(json.dumps(metadata))

    with run_weld([str(source)], config={"minecraft": "1.21.11"}) as ctx:
        assert not ctx.data.functions
        assert not ctx.assets
        assert len(ctx.data.overlays) == 1
        overlay = next(iter(ctx.data.overlays.values()))
        assert overlay.supported_formats == [61, 62]
        assert overlay.functions["test:main"].lines == ["say overlay"]
