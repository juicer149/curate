"""
Query layer.

This module provides editor-facing queries without any editor-state.

Key idea:
- The semantic model is stateless.
- Queries produce deterministic answers based on line coverage.

Provided queries:
- entities_at_line(root, line_no) -> tuple[Entity, ...]
- best_entity_at_line(root, line_no) -> Entity | None
- scope_at_line(root, line_no) -> Scope

Owner/parent queries (derived, no model recursion):
- parent_entity(root, entity) -> Entity | None
- direct_children(root, entity) -> tuple[Entity, ...]
- descendants(root, entity) -> tuple[Entity, ...]
"""

from __future__ import annotations

from typing import Iterable, Optional, Tuple, List

from .entity import Entity
from .line import Line
from .scope import Scope


# ================================================================
# Iterators
# ================================================================

def iter_scopes(root: Scope) -> Iterable[Scope]:
    yield root
    for c in root.children:
        yield from iter_scopes(c)


def iter_entities(root: Scope) -> Iterable[Entity]:
    for sc in iter_scopes(root):
        for e in sc.entities:
            yield e


# ================================================================
# Spans
# ================================================================

def _line_span(lines: Tuple[Line, ...]) -> tuple[int, int]:
    """
    Return (min_line, max_line) for a non-empty lines tuple.
    """
    return (lines[0].number, lines[-1].number)


def entity_span(e: Entity) -> Optional[tuple[int, int]]:
    """
    Span covering all lines belonging to the entity (head + body).
    Returns None if entity is empty (should not happen in normal extraction).
    """
    all_lines = e.all_lines
    if not all_lines:
        return None
    return _line_span(all_lines)


def _contains(outer: tuple[int, int], inner: tuple[int, int]) -> bool:
    oa, ob = outer
    ia, ib = inner
    return oa <= ia and ib <= ob


def _strictly_contains(outer: tuple[int, int], inner: tuple[int, int]) -> bool:
    oa, ob = outer
    ia, ib = inner
    return oa <= ia and ib <= ob and (oa < ia or ib < ob)


# ================================================================
# Line-based queries
# ================================================================

def entities_at_line(root: Scope, line_no: int) -> Tuple[Entity, ...]:
    """
    Return all entities whose span covers line_no.

    Order:
      - sorted by smallest span first (most local first)
      - tie-break by earlier start line
    """
    hits = []
    for e in iter_entities(root):
        span = entity_span(e)
        if not span:
            continue
        a, b = span
        if a <= line_no <= b:
            hits.append((b - a, a, e))

    hits.sort(key=lambda t: (t[0], t[1]))
    return tuple(e for _, _, e in hits)


def best_entity_at_line(root: Scope, line_no: int) -> Optional[Entity]:
    """
    Return the most local (smallest-span) entity covering line_no.
    """
    hits = entities_at_line(root, line_no)
    return hits[0] if hits else None


def scope_at_line(root: Scope, line_no: int) -> Scope:
    """
    Return the most local scope covering line_no.

    Note:
    - Scope coverage is determined by its lines span.
    - The smallest matching scope is returned.
    """
    candidates = []
    for sc in iter_scopes(root):
        if not sc.lines:
            continue
        a, b = _line_span(sc.lines)
        if a <= line_no <= b:
            candidates.append((b - a, a, sc))

    candidates.sort(key=lambda t: (t[0], t[1]))
    return candidates[0][2] if candidates else root


# ================================================================
# Owner / parent queries (derived)
# ================================================================

def parent_entity(root: Scope, entity: Entity) -> Optional[Entity]:
    """
    Return the closest (smallest-span) entity that strictly contains `entity`.

    This is the "owner" relation you want, but *derived*:
    - No recursion stored in the model
    - No cycles
    - Easy to serialize the model as-is
    """
    inner = entity_span(entity)
    if not inner:
        return None

    candidates: List[tuple[int, int, Entity]] = []
    for e in iter_entities(root):
        if e is entity:
            continue
        outer = entity_span(e)
        if not outer:
            continue
        if _strictly_contains(outer, inner):
            oa, ob = outer
            candidates.append((ob - oa, oa, e))

    candidates.sort(key=lambda t: (t[0], t[1]))
    return candidates[0][2] if candidates else None


def direct_children(root: Scope, entity: Entity) -> Tuple[Entity, ...]:
    """
    Return entities whose parent_entity(...) is exactly `entity`.
    """
    kids: List[tuple[int, int, Entity]] = []
    for e in iter_entities(root):
        if e is entity:
            continue
        p = parent_entity(root, e)
        if p is entity:
            sp = entity_span(e)
            if sp:
                a, b = sp
                kids.append((a, b, e))

    kids.sort(key=lambda t: (t[0], t[1]))
    return tuple(e for _, _, e in kids)


def descendants(root: Scope, entity: Entity) -> Tuple[Entity, ...]:
    """
    Return all entities strictly contained in `entity` (not just direct children).

    Useful for:
    - "fold everything inside this class"
    - "toggle minimum view inside current scope"
    """
    outer = entity_span(entity)
    if not outer:
        return tuple()

    out: List[tuple[int, int, Entity]] = []
    for e in iter_entities(root):
        if e is entity:
            continue
        inner = entity_span(e)
        if not inner:
            continue
        if _strictly_contains(outer, inner):
            a, b = inner
            out.append((a, b, e))

    out.sort(key=lambda t: (t[0], t[1]))
    return tuple(e for _, _, e in out)
