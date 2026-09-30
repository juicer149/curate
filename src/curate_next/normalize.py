"""curate_next.core.normalize — composable span normalization rules

Instead of repeating imperative "if chains", we treat normalization as small
rules that can be composed.

All normalizations operate on inclusive 1-based line spans: (start_line, end_line).

Rules
-----
- clamp_to_document(total_lines): confines span to [1..total_lines]
- clamp_to_parent(parent_start, parent_end): confines span within parent
- ensure_end_ge_start: makes (start,end) a valid (possibly degenerate) span

These rules are used by core.derive, not by producers.
"""

from __future__ import annotations

from typing import Callable, Tuple

Rule = Callable[[int, int], Tuple[int, int]]


def clamp_int(x: int, lo: int, hi: int) -> int:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def ensure_end_ge_start(start: int, end: int) -> Tuple[int, int]:
    if end < start:
        end = start
    return start, end


def clamp_to_document(total_lines: int) -> Rule:
    lo, hi = 1, max(1, int(total_lines))

    def rule(start: int, end: int) -> Tuple[int, int]:
        start = clamp_int(int(start), lo, hi)
        end = clamp_int(int(end), lo, hi)
        return ensure_end_ge_start(start, end)

    return rule


def clamp_to_parent(parent_start: int, parent_end: int) -> Rule:
    ps, pe = int(parent_start), int(parent_end)

    def rule(start: int, end: int) -> Tuple[int, int]:        
        if start < ps:
            start = ps
        if end > pe:
            end = pe
        return ensure_end_ge_start(start, end)

    return rule


def compose(*rules: Rule) -> Rule:
    def run(start: int, end: int) -> Tuple[int, int]:
        for r in rules:
            start, end = r(start, end)
        return start, end

    return run
