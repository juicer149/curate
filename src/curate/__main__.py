# src/curate/__main__.py
"""
Command-line adapter for Curate.

Role
----
This module is a thin CLI adapter:

- Translates CLI input into engine intent
- Invokes the folding engine
- Formats output for the caller

It does NOT:
- Interpret structure
- Apply folding semantics
- Special-case languages or editors

Design principle
----------------
"Adapters translate intent and format output. They do not contain logic."
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable

from .engine import fold
from .types import FoldMode, Range


def _read_source(path: str | None) -> str:
    if path is None or path == "-":
        return sys.stdin.read()
    return open(path, encoding="utf-8").read()


def _emit_text(ranges: Iterable[Range]) -> None:
    for start, end in ranges:
        print(f"{start}:{end}")


def _emit_json(ranges: Iterable[Range]) -> None:
    # JSON array of [start, end]
    print(json.dumps({"folds": list(ranges)}))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser("curate")

    parser.add_argument(
        "file",
        nargs="?",
        default="-",
        help="Source file (default: stdin)",
    )
    parser.add_argument(
        "--line",
        type=int,
        required=True,
        help="Cursor line (1-based)",
    )
    parser.add_argument(
        "--level",
        type=int,
        default=0,
        help="Ancestor level (0 = current scope)",
    )
    parser.add_argument(
        "--mode",
        choices=("self", "children"),
        default="children",
        help="Fold mode",
    )
    parser.add_argument(
        "--language",
        default="python",
        help="Language backend (default: python)",
    )
    parser.add_argument(
        "--output",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args(argv)

    source = _read_source(args.file)

    ranges = fold(
        source=source,
        cursor=args.line,
        level=args.level,
        mode=args.mode,      # FoldMode
        language=args.language,
    )

    if args.output == "json":
        _emit_json(ranges)
    else:
        _emit_text(ranges)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
