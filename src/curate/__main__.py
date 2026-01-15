# src/curate/__main__.py
"""
Command-line interface for curate.

Responsibilities:
- Parse CLI arguments
- Read source text (from file or stdin)
- Dispatch to the core engine
- Serialize results as text or JSON

Non-responsibilities:
- No structural logic
- No parsing or indexing
- No policy decisions

This file is intentionally thin and imperative.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable

from .engine import fold, query_scopes
from .types import Range


def _read_source(path: str | None) -> str:
    """
    Read source text.

    Pseudocode:
    - If path is "-" or None: read from stdin
    - Else: read file as UTF-8 text
    """
    if path is None or path == "-":
        return sys.stdin.read()
    return open(path, encoding="utf-8").read()


def _emit_text(ranges: Iterable[Range]) -> None:
    """
    Emit ranges as simple 'start:end' lines.

    Intended for:
    - shell pipelines
    - editor integrations
    """
    for a, b in ranges:
        print(f"{a}:{b}")


def _emit_json(ranges: Iterable[Range]) -> None:
    """
    Emit ranges as JSON.

    Output format:
    {
        "folds": [[start, end], ...]
    }
    """
    print(json.dumps({"folds": [list(r) for r in ranges]}))


def main(argv: list[str] | None = None) -> int:
    """
    CLI entry point.

    Pseudocode:
    - Parse arguments
    - Read source text
    - Either:
        - Run a structured query
        - Or run a convenience fold
    - Emit output
    """
    p = argparse.ArgumentParser("curate")

    p.add_argument("file", nargs="?", default="-", help="Source file (default: stdin)")
    p.add_argument("--line", type=int, required=True, help="Cursor line (1-based)")
    p.add_argument("--language", default="python", help="Language backend (default: python)")
    p.add_argument("--output", choices=("text", "json"), default="json", help="Output format")

    p.add_argument(
        "--mode",
        choices=("self", "children", "parent", "ancestors", "descendants"),
        default="children",
        help="Convenience folding mode (just a query wrapper)",
    )

    p.add_argument(
        "--query",
        default=None,
        help='Optional JSON QueryDict, e.g. \'{"axis":"siblings","kinds":["function"]}\'',
    )

    args = p.parse_args(argv)
    source = _read_source(args.file)

    if args.query:
        try:
            q = json.loads(args.query)
        except Exception as e:
            print(f"invalid --query JSON: {e}", file=sys.stderr)
            return 2
        ranges = query_scopes(source=source, cursor=args.line, query=q, language=args.language)
    else:
        ranges = fold(source=source, cursor=args.line, mode=args.mode, language=args.language)

    (_emit_json if args.output == "json" else _emit_text)(ranges)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
