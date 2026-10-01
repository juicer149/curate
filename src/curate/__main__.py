"""
Command-line interface for Curate.

    curate chain FILE --line N [--language NAME] [--producer treesitter]

Prints the structural path at a line as JSON, innermost scope first:

    {"line": 16, "chain": [
        {"address": [0, 1], "label": "if", "start": 15, "end": 17},
        {"address": [0], "label": "function", "start": 7, "end": 19}
    ]}

Lines are 1-based and inclusive. FILE may be "-" for stdin.
Without --language the language comes from the file suffix (.py, .md);
stdin has no suffix, so it needs --language.
The CLI only reads, compiles and serializes; structure comes from the core.
"""

from __future__ import annotations

import argparse
import json
import sys

from .compile import compile_scopes
from .relations import chain


def _read_source(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _language(args: argparse.Namespace) -> str | None:
    """--language if given, else the file suffix; None if neither tells."""
    if args.language:
        return args.language.lower()
    if args.file == "-":
        return None
    from .producers.treesitter.languages import language_for_path

    return language_for_path(args.file)


def _cmd_chain(args: argparse.Namespace) -> int:
    language = _language(args)
    if language is None:
        what = "stdin" if args.file == "-" else f"'{args.file}'"
        print(f"curate: cannot tell the language of {what}; pass --language", file=sys.stderr)
        return 2

    if args.producer == "treesitter":
        from .producers.treesitter.languages import resolve

        if resolve(language) is None:
            print(f"curate: no structure support for language '{language}'", file=sys.stderr)
            return 2

    source = _read_source(args.file)

    errors: list[str] = []
    scopes = compile_scopes(
        source=source,
        language=language,
        producer=args.producer,
        on_error=lambda e: errors.append(f"{type(e).__name__}: {e}"),
    )
    if errors:
        print(f"curate: producer '{args.producer}' failed: {errors[0]}", file=sys.stderr)
        return 1

    path = chain(scopes, args.line)
    print(json.dumps({
        "line": args.line,
        "chain": [
            {
                "address": list(s.address.parts),
                "label": s.label,
                "start": s.span.start,
                "end": s.span.end,
            }
            for s in path
        ],
    }))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="curate")
    sub = parser.add_subparsers(dest="command", required=True)

    p_chain = sub.add_parser("chain", help="structural path at a line, innermost first")
    p_chain.add_argument("file", help='source file, or "-" for stdin')
    p_chain.add_argument("--line", type=int, required=True, help="1-based line")
    p_chain.add_argument("--language", help="e.g. python, markdown (default: from the file suffix)")
    p_chain.add_argument("--producer", default="treesitter")
    p_chain.set_defaults(func=_cmd_chain)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
