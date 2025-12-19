"""
Command-line adapter.

Place in pipeline:
- Converts CLI input into a Config object
- Delegates all semantics to engine.fold()
- Serializes fold ranges as JSON

This module is an adapter:
- no structural logic
- no folding logic
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import Config
from .engine import fold


def _read_content(path: str | None) -> str:
    """
    Read source content.

    If path is "-", read from stdin.
    Otherwise read file contents as UTF-8.
    """
    if path is None or path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8")


def main(argv=None) -> int:
    p = argparse.ArgumentParser("curate")

    p.add_argument(
        "file",
        nargs="?",
        default="-",
        help="Source file path or '-' for stdin",
    )
    p.add_argument("--line", type=int, required=True)
    p.add_argument("--level", type=int, default=0)
    p.add_argument(
        "--type",
        dest="file_type",
        default="python",
        help="Source language identifier",
    )

    view = p.add_mutually_exclusive_group()
    view.add_argument(
        "-f",
        "--children",
        action="store_true",
        help="Fold children scopes (default)",
    )
    view.add_argument(
        "-F",
        "--self",
        dest="fold_self",
        action="store_true",
        help="Fold entire target scope",
    )

    args = p.parse_args(argv)

    content = _read_content(args.file)

    cfg = Config(
        file_type=args.file_type,
        content=content,
        cursor=args.line,
        level=args.level,
        fold_children=not args.fold_self,
    )

    ranges = fold(cfg)

    print(
        json.dumps(
            {
                "folds": [{"start": a, "end": b} for a, b in ranges],
            }
        )
    )
    return 0
