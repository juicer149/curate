"""curate.query — single-entry structural query API

This module provides a small, deterministic query surface meant for:
- editors
- AI context selection
- structural extraction

It is intentionally NOT a policy engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Optional, Sequence

from .facts import Scope, ScopeSet
from .compile import compile_scope_set
from .index import Index, build_index, scope_at_line
from . import relations as rel

Axis = Literal["self", "children", "parent", "ancestors", "descendants", "siblings"]
Range = tuple[int, int]


@dataclass(frozen=True, slots=True)
class Query:
    axis: Axis
    kinds: Optional[tuple[str, ...]] = None
    max_items: int = 50


def _filter_kinds(scopes: Iterable[Scope], kinds: Optional[tuple[str, ...]]) -> list[Scope]:
    if not kinds:
        return list(scopes)
    allowed = set(kinds)
    return [s for s in scopes if s.kind in allowed]


def _unique_sorted_ranges(scopes: Sequence[Scope]) -> list[Range]:
    seen: set[Range] = set()
    out: list[Range] = []
    for s in scopes:
        r = (s.start, s.end)
        if r not in seen:
            seen.add(r)
            out.append(r)
    out.sort(key=lambda r: (r[0], r[1]))
    return out


def query_ranges(
    *,
    source: str,
    cursor: int,
    query: Query,
    language: str = "default",
) -> list[Range]:
    """
    Main entry point: source + cursor + query -> list of safe (start,end) line ranges.

    Guarantees:
    - deterministic
    - safe slicing ranges (1-based inclusive)
    - never crashes for any cursor
    - no duplicate ranges
    - sorted output
    """
    scopeset: ScopeSet = compile_scope_set(source=source, language=language)
    idx: Index = build_index(scopeset)

    # Normalize cursor to be at least 1; scope_at_line handles out-of-range naturally.
    cur_line = max(1, int(cursor))
    self_scope = scope_at_line(idx, cur_line)
    if self_scope is None:
        return []

    axis = query.axis

    if axis == "self":
        scopes = [self_scope]
    elif axis == "children":
        scopes = list(rel.children(idx, self_scope))
    elif axis == "parent":
        p = rel.parent(idx, self_scope)
        scopes = [] if p is None else [p]
    elif axis == "ancestors":
        scopes = list(rel.ancestors(idx, self_scope))
    elif axis == "descendants":
        scopes = list(rel.descendants(idx, self_scope))
    elif axis == "siblings":
        scopes = list(rel.siblings(idx, self_scope))
    else:
        scopes = []

    scopes = _filter_kinds(scopes, query.kinds)
    if query.max_items > 0:
        scopes = scopes[: query.max_items]

    return _unique_sorted_ranges(scopes)


def fold(
    *,
    source: str,
    cursor: int,
    mode: Literal["self", "children"] = "self",
    language: str = "default",
) -> list[Range]:
    """
    Convenience API for editor-like folding.

    NOTE:
        This is a preset wrapper over query_ranges().
        For general structural selection, use query_ranges() directly.
    """
    axis: Axis = "self" if mode == "self" else "children"
    return query_ranges(source=source, cursor=cursor, query=Query(axis=axis), language=language)
