"""
Command-line interface for Curate.

    curate chain FILE --line N [--language NAME] [--producer treesitter]
    curate outline FILE [--closed] [--language NAME] [--producer treesitter]

`chain` prints the structural path at a line as JSON, innermost first.
"outline" says how the scope shows in the file's outline ("open",
"closed" or null):

    {"line": 16, "chain": [
        {"address": [0, 1], "label": "if", "start": 15, "end": 17, "outline": null},
        {"address": [0], "label": "function", "start": 7, "end": 19, "outline": "closed"}
    ]}

`outline` prints the line ranges to fold so only the skeleton shows
(see curate.outline); they never overlap:

    {"folds": [{"start": 7, "end": 19}, {"start": 23, "end": 24}]}

With --closed every entry folds whole, so a class is one line too.

A scope or fold whose naming line is not its first line also has "head"
(a decorated definition starts at its decorator; "head" is the `def`).

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
from .facts import ScopeSet
from .outline import outline_folds
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


class _Fail(Exception):
    """A message for stderr and an exit code."""

    def __init__(self, message: str, code: int) -> None:
        super().__init__(message)
        self.code = code


def _compile(args: argparse.Namespace) -> tuple[ScopeSet, dict[str, str]]:
    """Read, compile and return the scopes with the language's outline kinds."""
    language = _language(args)
    if language is None:
        what = "stdin" if args.file == "-" else f"'{args.file}'"
        raise _Fail(f"cannot tell the language of {what}; pass --language", 2)

    kinds: dict[str, str] = {}
    if args.producer == "treesitter":
        from .producers.treesitter.languages import get_spec

        spec = get_spec(language)
        if spec is None:
            raise _Fail(f"no structure support for language '{language}'", 2)
        kinds = dict(spec.outline)

    errors: list[str] = []
    scopes = compile_scopes(
        source=_read_source(args.file),
        language=language,
        producer=args.producer,
        on_error=lambda e: errors.append(f"{type(e).__name__}: {e}"),
    )
    if errors:
        raise _Fail(f"producer '{args.producer}' failed: {errors[0]}", 1)
    return scopes, kinds


def _head(head: int, start: int) -> dict[str, int]:
    """`{"head": n}` when the line naming a scope is not its first line."""
    return {"head": head} if head != start else {}


def _cmd_chain(args: argparse.Namespace) -> int:
    scopes, kinds = _compile(args)
    print(json.dumps({
        "line": args.line,
        "chain": [
            {
                "address": list(s.address.parts),
                "label": s.label,
                "start": s.span.start,
                "end": s.span.end,
                "outline": kinds.get(s.label),
                **_head(s.head_line, s.span.start),
            }
            for s in chain(scopes, args.line)
        ],
    }))
    return 0


def _cmd_outline(args: argparse.Namespace) -> int:
    scopes, kinds = _compile(args)
    if args.closed:
        kinds = {label: "closed" for label in kinds}
    # Every outline fold starts where an entry starts.
    heads = {s.span.start: s.head for s in scopes.scopes if s.head is not None}
    print(json.dumps({
        "folds": [
            {"start": f.start, "end": f.end, **_head(heads.get(f.start, f.start), f.start)}
            for f in outline_folds(scopes, kinds)
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

    p_outline = sub.add_parser("outline", help="line ranges to fold for the file's outline")
    p_outline.add_argument("file", help='source file, or "-" for stdin')
    p_outline.add_argument("--language", help="e.g. python, markdown (default: from the file suffix)")
    p_outline.add_argument("--producer", default="treesitter")
    p_outline.add_argument(
        "--closed",
        action="store_true",
        help="fold every outline entry whole (classes too: one line each)",
    )
    p_outline.set_defaults(func=_cmd_outline)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except _Fail as e:
        print(f"curate: {e}", file=sys.stderr)
        return e.code


if __name__ == "__main__":
    raise SystemExit(main())
