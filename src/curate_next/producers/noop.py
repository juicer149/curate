"""
curate_next.producers.noop — fallback producer (raw)

Noop produces a single module-level RawScope spanning the entire file.

This ensures:
- every file has at least one raw structural fact
- producers remain responsible for declaring structure
- core does not need to special-case empty input
"""

from __future__ import annotations

from curate_next.facts import Position, RawScope, RawScopeSet


def _total_lines(source: str) -> int:
    return max(1, source.count("\n") + 1)


def build_raw_scope_set(*, source: str, language: str) -> RawScopeSet:
    total = _total_lines(source)

    module = RawScope(
        label="module",
        start=Position(1),
        end=Position(total),
    )

    return RawScopeSet((module,))
