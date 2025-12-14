"""
Fold plan.

A fold plan is a pure, deterministic answer:
- which line ranges should be hidden for a given view mode

This allows you to test behaviour before Lua integration.

Representation:
- a fold range is (start_line, end_line), inclusive
- ranges are normalized and non-overlapping

Policy:
- FULL: no folds
- MINIMUM: fold every entity.body (if any)
- DOCS_ONLY: fold all non-doc lines
- CODE_ONLY: fold all doc lines
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple

from .line import Line
from .scope import Scope
from .views import ViewMode
from .query import iter_entities


Range = Tuple[int, int]


def _normalize(ranges: List[Range]) -> List[Range]:
    if not ranges:
        return []
    ranges.sort(key=lambda r: (r[0], r[1]))
    out = [ranges[0]]
    for a, b in ranges[1:]:
        la, lb = out[-1]
        if a <= lb + 1:
            out[-1] = (la, max(lb, b))
        else:
            out.append((a, b))
    return out


def _span(lines: Tuple[Line, ...]) -> Range:
    return (lines[0].number, lines[-1].number)


def fold_plan_for_view(root: Scope, mode: ViewMode) -> Tuple[Range, ...]:
    if mode == ViewMode.FULL:
        return tuple()

    folds: List[Range] = []

    if mode == ViewMode.MINIMUM:
        for e in iter_entities(root):
            if e.body:
                folds.append(_span(e.body))
        return tuple(_normalize(folds))

    if mode == ViewMode.DOCS_ONLY:
        # fold everything that is NOT doc
        start = None
        for l in root.lines:
            is_doc = "doc" in l.kinds
            if not is_doc:
                if start is None:
                    start = l.number
            else:
                if start is not None:
                    folds.append((start, l.number - 1))
                    start = None
        if start is not None:
            folds.append((start, root.lines[-1].number))
        return tuple(_normalize(folds))

    if mode == ViewMode.CODE_ONLY:
        # fold everything that IS doc
        start = None
        for l in root.lines:
            is_doc = "doc" in l.kinds
            if is_doc:
                if start is None:
                    start = l.number
            else:
                if start is not None:
                    folds.append((start, l.number - 1))
                    start = None
        if start is not None:
            folds.append((start, root.lines[-1].number))
        return tuple(_normalize(folds))

    raise ValueError(f"Unknown view mode: {mode}")
