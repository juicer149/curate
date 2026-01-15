"""Minimal CLI for Curate.

Examples:
  python -m curate --file path.py --cursor 42 --axis descendants --kinds function_definition class_definition
  cat path.py | python -m curate --cursor 10 --axis self
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from .query import Query, query_ranges


def _read_source(path: Optional[str]) -> str:
    if path:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    return sys.stdin.read()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="curate", description="Curate: structural scope ranges.")
    p.add_argument("--file", "-f", default=None, help="Read source from file (otherwise stdin).")
    p.add_argument("--language", "-l", default="default", help="Language key (e.g. python).")
    p.add_argument("--cursor", "-c", type=int, required=True, help="1-based cursor line.")
    p.add_argument("--axis", default="self", choices=["self", "children", "parent", "ancestors", "descendants", "siblings"])
    p.add_argument("--kinds", nargs="*", default=None, help="Optional kinds filter (Tree-sitter node.type strings).")
    p.add_argument("--max-items", type=int, default=50, help="Max number of returned ranges.")
    p.add_argument("--json", action="store_true", help="Output JSON (default).")

    args = p.parse_args(argv)
    source = _read_source(args.file)

    q = Query(
        axis=args.axis,
        kinds=None if not args.kinds else tuple(args.kinds),
        max_items=max(0, int(args.max_items)),
    )

    ranges = query_ranges(
        source=source,
        cursor=args.cursor,
        query=q,
        language=args.language,
    )

    # Always JSON for machine consumption; --json kept for compatibility.
    sys.stdout.write(json.dumps(ranges, indent=2))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
