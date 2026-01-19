"""curate.relations.core — algebraic relations over Scope facts.

This module defines structural relations derived solely from Scope.address.

Important properties:
- no interpretation
- no semantic classification
- no indexes or caches
- correctness depends only on Scope.address invariants

All relations are derived algebraically from hierarchical addresses.
"""

from __future__ import annotations

from typing import Tuple

from ..facts import Scope, ScopeAddress, ScopeSet


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _is_parent(parent_address: ScopeAddress, child_address: ScopeAddress) -> bool:
    """
    Return True if parent_address is the immediate parent of child_address.

    parent_address == child_address[:-1]
    """
    return (
        len(child_address) == len(parent_address) + 1
        and child_address[:-1] == parent_address
    )


def _is_ancestor(
    ancestor_address: ScopeAddress,
    descendant_address: ScopeAddress,
) -> bool:
    """
    Return True if ancestor_address is a (non-equal) ancestor of descendant_address.
    """
    return (
        len(descendant_address) > len(ancestor_address)
        and descendant_address[: len(ancestor_address)] == ancestor_address
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
    parent_addr = scope.parent_address
    if parent_addr is None:
        return None

    for s in scopes:
        if s.address == parent_addr:
            return s
    return None


def children(scopes: ScopeSet, scope: Scope) -> Tuple[Scope, ...]:
    """
    Return direct children of `scope`.

    Children are scopes whose address is exactly one level deeper
    and share the same prefix.

    Ordering is deterministic according to ScopeSet ordering.
    """
    return tuple(
        s for s in scopes
        if _is_parent(scope.address, s.address)
    )


def siblings(scopes: ScopeSet, scope: Scope) -> Tuple[Scope, ...]:
    """
    Return siblings of `scope` (same parent), excluding `scope`.

    Root scope has no siblings.
    """
    parent_addr = scope.parent_address
    if parent_addr is None:
        return ()

    return tuple(
        s for s in scopes
        if s.address != scope.address and s.parent_address == parent_addr
    )


def ancestors(scopes: ScopeSet, scope: Scope) -> Tuple[Scope, ...]:
    """
    Return all ancestors of `scope`, ordered from nearest parent to root.

    Example:
        scope.address = (0, 1, 2, 3)

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

    A descendant is any scope whose address starts with scope.address
    and is strictly longer.
    """
    base = scope.address
    return tuple(
        s for s in scopes
        if _is_ancestor(base, s.address)
    )


# ---------------------------------------------------------------------------
# Convenience predicates (still structural)
# ---------------------------------------------------------------------------

def is_root(scope: Scope) -> bool:
    """Return True if scope is the root scope."""
    return len(scope.address) == 1


def depth(scope: Scope) -> int:
    """
    Return structural depth of the scope.

    Root depth == 0.
    """
    return len(scope.address) - 1
