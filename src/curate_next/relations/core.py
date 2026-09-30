"""
curate_next.relations.core — algebraic relations over derived ScopeSet

Relations are derived purely from Address algebra and ScopeSet invariants.

No interpretation.
No indexes beyond ScopeSet.by_address().
"""

from __future__ import annotations

from typing import Tuple, List

from ..facts import Scope, ScopeSet
from ..address import Address


# ---------------------------------------------------------------------------
# Core relations
# ---------------------------------------------------------------------------

def parent(scopes: ScopeSet, scope: Scope) -> Scope | None:
    """Return the immediate parent of `scope`, or None if it is root."""
    addr = scope.parent_address
    if addr is None:
        return None
    return scopes.by_address(addr)


def children(scopes: ScopeSet, scope: Scope) -> Tuple[Scope, ...]:
    """
    Return direct children of `scope`.

    Relies on the invariant that children are assigned contiguously
    as (address + 0), (address + 1), ..., with no gaps.
    """
    out: List[Scope] = []
    i = 0
    while True:
        child_addr = scope.address + i
        child = scopes.by_address(child_addr)
        if child is None:
            break
        out.append(child)
        i += 1
    return tuple(out)


def ancestors(scopes: ScopeSet, scope: Scope) -> Tuple[Scope, ...]:
    """
    Return all ancestors of `scope`, ordered from nearest parent to root.
    """
    out: List[Scope] = []
    cur = scope
    while True:
        p = parent(scopes, cur)
        if p is None:
            break
        out.append(p)
        cur = p
    return tuple(out)


def descendants(scopes: ScopeSet, scope: Scope) -> Tuple[Scope, ...]:
    """
    Return all descendants of `scope`, in deterministic order.

    A descendant is any scope whose address has `scope.address` as a prefix
    and is strictly deeper.
    """
    base = scope.address.parts
    n = len(base)
    return tuple(
        s for s in scopes
        if len(s.address.parts) > n and s.address.parts[:n] == base
    )


# ---------------------------------------------------------------------------
# Convenience predicates
# ---------------------------------------------------------------------------

def is_root(scope: Scope) -> bool:
    """Return True if scope is the root scope."""
    return scope.address.is_root


def depth(scope: Scope) -> int:
    """Return structural depth of the scope (root == 0)."""
    return scope.address.depth()
