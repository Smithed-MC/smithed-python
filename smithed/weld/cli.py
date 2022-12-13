from pathlib import Path
import time
from argparse import ArgumentParser
from typing import Any

from beet import run_beet
from beet.core.utils import FileSystemPath


def main():
    parser = ArgumentParser()
    parser.add_argument("packs", type=str, nargs="+")
    parser.add_argument("--output", type=str, default="dist")
    args = parser.parse_args()

    t0 = time.perf_counter()
    with run_weld(args.packs, args.output) as ctx:
        ...
    t1 = time.perf_counter()

    print("Success Merging", f"{t1-t0:0.2f}s")


def run_weld(packs: list[FileSystemPath] = [], output: str = "", directory: FileSystemPath = ""):
    packs = packs or list(path.name for path in Path(directory).glob("*"))

    return run_beet(
        {
            "pipeline": [
                "weld.setup",
                *[{"data_pack": {"load": pack}} for pack in packs],
                "weld",
            ],
        }
        | ({"output": output} if output else {})
        | ({"directory": directory} if directory else {})
    )
