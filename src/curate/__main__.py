from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable

from .engine import fold
from .types import Range


def _read_source(path: str | None) -> str:
    if path is None or path == "-":
        return sys.stdin.read()
    return open(path, encoding="utf-8").read()


def _emit_text(ranges: Iterable[Range]) -> None:
    for a, b in ranges:
        print(f"{a}:{b}")


def _emit_json(ranges: Iterable[Range]) -> None:
    print(json.dumps({"folds": [list(r) for r in ranges]}))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser("curate")
    p.add_argument("file", nargs="?", default="-")
    p.add_argument("--line", type=int, required=True)
    p.add_argument("--level", type=int, default=0)
    p.add_argument("--mode", choices=("self", "children"), default="children")
    p.add_argument("--language", default="python")
    p.add_argument("--output", choices=("text", "json"), default="text")

    args = p.parse_args(argv)
    source = _read_source(args.file)

    ranges = fold(
        source=source,
        cursor=args.line,
        level=args.level,
        mode=args.mode,
        language=args.language,
    )

    (_emit_json if args.output == "json" else _emit_text)(ranges)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
