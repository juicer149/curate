"""curate.relations.core — algebraic relations over Scope facts.

This module defines structural relations derived solely from Scope.id.

Important properties:
- no interpretation
- no semantic classification
- no indexes or caches
- correctness depends only on Scope.id invariants

All relations are derived algebraically.
"""

from __future__ import annotations

from typing import Tuple

from ..facts import Scope, ScopeId, ScopeSet


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _is_parent(parent_id: ScopeId, child_id: ScopeId) -> bool:
    """
    Return True if parent_id is the immediate parent of child_id.

    parent_id == child_id[:-1]
    """
    return (
        len(child_id) == len(parent_id) + 1
        and child_id[:-1] == parent_id
    )


def _is_ancestor(ancestor_id: ScopeId, descendant_id: ScopeId) -> bool:
    """
    Return True if ancestor_id is a (non-equal) ancestor of descendant_id.
    """
    return (
        len(descendant_id) > len(ancestor_id)
        and descendant_id[:len(ancestor_id)] == ancestor_id
    )


# ---------------------------------------------------------------------------
# Public relations API
# ---------------------------------------------------------------------------

def parent(scopes: ScopeSet, scope: Scope) -> Scope | None:
    """
    Return the immediate parent of `scope`, or None if it is root.

    Invariants:
    - At most one parent exists
    - Root scope has no parent
    """
    pid = scope.parent_id
    if pid is None:
        return None

    for s in scopes:
        if s.id == pid:
            return s
    return None


def children(scopes: ScopeSet, scope: Scope) -> Tuple[Scope, ...]:
    """
    Return direct children of `scope`.

    Children are scopes whose id is exactly one level deeper
    and share the same prefix.

    Ordering is deterministic according to ScopeSet ordering.
    """
    return tuple(
        s for s in scopes
        if _is_parent(scope.id, s.id)
    )


def siblings(scopes: ScopeSet, scope: Scope) -> Tuple[Scope, ...]:
    """
    Return siblings of `scope` (same parent), excluding `scope`.

    Root scope has no siblings.
    """
    pid = scope.parent_id
    if pid is None:
        return ()

    return tuple(
        s for s in scopes
        if s.id != scope.id and s.parent_id == pid
    )


def ancestors(scopes: ScopeSet, scope: Scope) -> Tuple[Scope, ...]:
    """
    Return all ancestors of `scope`, ordered from nearest parent to root.

    Example:
        scope.id = (0, 1, 2, 3)

        ancestors = [
            (0, 1, 2),
            (0, 1),
            (0,)
        ]
    """
    out: list[Scope] = []
    cur = scope

    while True:
        p = parent(scopes, cur)
        if p is None:
            return tuple(out)
        out.append(p)
        cur = p


def descendants(scopes: ScopeSet, scope: Scope) -> Tuple[Scope, ...]:
    """
    Return all descendants of `scope` (depth-first, deterministic).

    A descendant is any scope whose id starts with scope.id
    and is strictly longer.
    """
    base = scope.id
    return tuple(
        s for s in scopes
        if _is_ancestor(base, s.id)
    )


# ---------------------------------------------------------------------------
# Convenience predicates (still structural)
# ---------------------------------------------------------------------------

def is_root(scope: Scope) -> bool:
    """Return True if scope is the root scope."""
    return len(scope.id) == 1


def depth(scope: Scope) -> int:
    """
    Return structural depth of the scope.

    Root depth == 0.
    """
    return len(scope.id) - 1
